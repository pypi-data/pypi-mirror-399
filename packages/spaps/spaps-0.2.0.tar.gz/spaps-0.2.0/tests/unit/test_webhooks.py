"""Tests for SPAPS webhook verification."""

import json
import time
from typing import Any, Dict

import pytest

from spaps_client.webhooks import (
    EntitlementGrantedEvent,
    EntitlementRenewedEvent,
    SpapsWebhookPayload,
    WebhookVerificationError,
    generate_test_signature,
    parse_entitlement_event,
    verify_spaps_webhook,
)


@pytest.fixture()
def webhook_secret() -> str:
    return "whsec_test_secret_key"


@pytest.fixture()
def sample_payload() -> Dict[str, Any]:
    return {
        "id": "evt_abc123",
        "type": "entitlement.granted",
        "schema_version": 1,
        "application_id": "app_123",
        "created_at": "2025-01-09T10:30:00Z",
        "data": {
            "entitlement_id": "ent_xyz",
            "user_id": "user_456",
            "email": None,
            "entitlement_key": "premium_access",
            "source": "stripe_subscription",
            "starts_at": "2025-01-01T00:00:00Z",
            "ends_at": "2025-02-01T00:00:00Z",
            "metadata": {},
        },
    }


class TestVerifySpapsWebhook:
    """Tests for verify_spaps_webhook function."""

    def test_valid_signature(
        self,
        webhook_secret: str,
        sample_payload: Dict[str, Any],
    ) -> None:
        """Test verification with valid signature."""
        timestamp = int(time.time())
        body = json.dumps(sample_payload)
        signature = generate_test_signature(sample_payload, webhook_secret, timestamp)

        result = verify_spaps_webhook(
            body,
            signature,
            webhook_secret,
            timestamp=timestamp,
        )

        assert isinstance(result, SpapsWebhookPayload)
        assert result.id == "evt_abc123"
        assert result.type == "entitlement.granted"
        assert result.schema_version == 1

    def test_valid_signature_with_bytes(
        self,
        webhook_secret: str,
        sample_payload: Dict[str, Any],
    ) -> None:
        """Test verification with bytes body."""
        timestamp = int(time.time())
        body = json.dumps(sample_payload).encode("utf-8")
        signature = generate_test_signature(sample_payload, webhook_secret, timestamp)

        result = verify_spaps_webhook(
            body,
            signature,
            webhook_secret,
            timestamp=timestamp,
        )

        assert result.id == "evt_abc123"

    def test_invalid_signature_format(
        self,
        webhook_secret: str,
        sample_payload: Dict[str, Any],
    ) -> None:
        """Test rejection of invalid signature format."""
        body = json.dumps(sample_payload)

        with pytest.raises(WebhookVerificationError) as exc_info:
            verify_spaps_webhook(body, "invalid_format", webhook_secret)

        assert exc_info.value.code == "INVALID_FORMAT"

    def test_invalid_signature_format_missing_v1(
        self,
        webhook_secret: str,
        sample_payload: Dict[str, Any],
    ) -> None:
        """Test rejection of signature without v1."""
        body = json.dumps(sample_payload)

        with pytest.raises(WebhookVerificationError) as exc_info:
            verify_spaps_webhook(body, "t=12345", webhook_secret)

        assert exc_info.value.code == "INVALID_FORMAT"

    def test_expired_signature(
        self,
        webhook_secret: str,
        sample_payload: Dict[str, Any],
    ) -> None:
        """Test rejection of expired signature."""
        old_timestamp = int(time.time()) - 600  # 10 minutes ago
        body = json.dumps(sample_payload)
        signature = generate_test_signature(sample_payload, webhook_secret, old_timestamp)

        current_time = int(time.time())
        with pytest.raises(WebhookVerificationError) as exc_info:
            verify_spaps_webhook(
                body,
                signature,
                webhook_secret,
                timestamp=current_time,
            )

        assert exc_info.value.code == "SIGNATURE_EXPIRED"

    def test_future_timestamp(
        self,
        webhook_secret: str,
        sample_payload: Dict[str, Any],
    ) -> None:
        """Test rejection of future timestamp."""
        future_timestamp = int(time.time()) + 600  # 10 minutes ahead
        body = json.dumps(sample_payload)
        signature = generate_test_signature(sample_payload, webhook_secret, future_timestamp)

        current_time = int(time.time())
        with pytest.raises(WebhookVerificationError) as exc_info:
            verify_spaps_webhook(
                body,
                signature,
                webhook_secret,
                timestamp=current_time,
            )

        assert exc_info.value.code == "TIMESTAMP_FUTURE"

    def test_wrong_secret(
        self,
        sample_payload: Dict[str, Any],
    ) -> None:
        """Test rejection with wrong secret."""
        timestamp = int(time.time())
        body = json.dumps(sample_payload)
        signature = generate_test_signature(sample_payload, "correct_secret", timestamp)

        with pytest.raises(WebhookVerificationError) as exc_info:
            verify_spaps_webhook(
                body,
                signature,
                "wrong_secret",
                timestamp=timestamp,
            )

        assert exc_info.value.code == "INVALID_SIGNATURE"

    def test_tampered_payload(
        self,
        webhook_secret: str,
        sample_payload: Dict[str, Any],
    ) -> None:
        """Test rejection of tampered payload."""
        timestamp = int(time.time())
        signature = generate_test_signature(sample_payload, webhook_secret, timestamp)

        # Tamper with payload
        sample_payload["data"]["entitlement_key"] = "hacked_access"
        tampered_body = json.dumps(sample_payload)

        with pytest.raises(WebhookVerificationError) as exc_info:
            verify_spaps_webhook(
                tampered_body,
                signature,
                webhook_secret,
                timestamp=timestamp,
            )

        assert exc_info.value.code == "INVALID_SIGNATURE"

    def test_invalid_json(
        self,
        webhook_secret: str,
    ) -> None:
        """Test rejection of invalid JSON."""
        body = "not valid json {"
        # Generate a valid signature for the malformed body
        timestamp = int(time.time())
        signature_base = f"{timestamp}.{body}"
        import hashlib
        import hmac as hmac_mod

        hmac_hex = hmac_mod.new(
            webhook_secret.encode("utf-8"),
            signature_base.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        signature = f"t={timestamp},v1={hmac_hex}"

        with pytest.raises(WebhookVerificationError) as exc_info:
            verify_spaps_webhook(body, signature, webhook_secret, timestamp=timestamp)

        assert exc_info.value.code == "INVALID_JSON"

    def test_custom_max_age(
        self,
        webhook_secret: str,
        sample_payload: Dict[str, Any],
    ) -> None:
        """Test custom max age."""
        # 8 minutes ago
        old_timestamp = int(time.time()) - 480
        body = json.dumps(sample_payload)
        signature = generate_test_signature(sample_payload, webhook_secret, old_timestamp)

        current_time = int(time.time())

        # Should fail with default 5 minute max age
        with pytest.raises(WebhookVerificationError):
            verify_spaps_webhook(
                body,
                signature,
                webhook_secret,
                timestamp=current_time,
            )

        # Should pass with 10 minute max age
        result = verify_spaps_webhook(
            body,
            signature,
            webhook_secret,
            max_age_seconds=600,
            timestamp=current_time,
        )
        assert result.id == "evt_abc123"


class TestParseEntitlementEvent:
    """Tests for parse_entitlement_event function."""

    def test_parse_granted_event(self, sample_payload: Dict[str, Any]) -> None:
        """Test parsing entitlement.granted event."""
        payload = SpapsWebhookPayload.model_validate(sample_payload)
        event = parse_entitlement_event(payload)

        assert isinstance(event, EntitlementGrantedEvent)
        assert event.type == "entitlement.granted"
        assert event.data.entitlement_key == "premium_access"

    def test_parse_renewed_event(self, sample_payload: Dict[str, Any]) -> None:
        """Test parsing entitlement.renewed event."""
        sample_payload["type"] = "entitlement.renewed"
        payload = SpapsWebhookPayload.model_validate(sample_payload)
        event = parse_entitlement_event(payload)

        assert isinstance(event, EntitlementRenewedEvent)
        assert event.type == "entitlement.renewed"

    def test_parse_unknown_event_returns_none(self, sample_payload: Dict[str, Any]) -> None:
        """Test that unknown event types return None."""
        sample_payload["type"] = "user.login"
        payload = SpapsWebhookPayload.model_validate(sample_payload)
        event = parse_entitlement_event(payload)

        assert event is None


class TestGenerateTestSignature:
    """Tests for generate_test_signature function."""

    def test_signature_format(self) -> None:
        """Test that generated signature has correct format."""
        payload = {"test": "data"}
        signature = generate_test_signature(payload, "secret", timestamp=1704800000)

        assert signature.startswith("t=1704800000,v1=")
        assert len(signature) == len("t=1704800000,v1=") + 64  # 64 hex chars

    def test_deterministic(self) -> None:
        """Test that same inputs produce same output."""
        payload = {"test": "data"}
        sig1 = generate_test_signature(payload, "secret", timestamp=1704800000)
        sig2 = generate_test_signature(payload, "secret", timestamp=1704800000)

        assert sig1 == sig2

    def test_different_secrets(self) -> None:
        """Test that different secrets produce different signatures."""
        payload = {"test": "data"}
        sig1 = generate_test_signature(payload, "secret1", timestamp=1704800000)
        sig2 = generate_test_signature(payload, "secret2", timestamp=1704800000)

        assert sig1 != sig2
