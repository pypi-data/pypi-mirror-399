"""Tests for the entitlements client."""

from typing import Any, Dict

import pytest
import respx
from httpx import Response

from spaps_client.entitlements import (
    Entitlement,
    EntitlementChangesResponse,
    EntitlementsClient,
    EntitlementsError,
    ManualGrantParams,
    PurchaseHistoryItem,
)


@pytest.fixture()
def base_url() -> str:
    return "https://api.sweetpotato.dev"


@pytest.fixture()
def api_key() -> str:
    return "test_key_local_dev_only"


@pytest.fixture()
def access_token() -> str:
    return "access-token"


@pytest.fixture()
def entitlements_client(base_url: str, api_key: str, access_token: str) -> EntitlementsClient:
    return EntitlementsClient(base_url=base_url, api_key=api_key, access_token=access_token)


@pytest.fixture()
def sample_entitlement() -> Dict[str, Any]:
    return {
        "id": "ent_abc123",
        "application_id": "app_123",
        "beneficiary_user_id": "user_456",
        "beneficiary_email": None,
        "entitlement_key": "premium_access",
        "source": "stripe_subscription",
        "starts_at": "2025-01-01T00:00:00Z",
        "ends_at": "2025-02-01T00:00:00Z",
        "revoked_at": None,
        "crypto_invoice_id": None,
        "stripe_subscription_id": "sub_xyz",
        "stripe_session_id": None,
        "stripe_invoice_id": None,
        "stripe_product_id": "prod_abc",
        "manual_grant_id": None,
        "manual_grant_reason": None,
        "granted_by_user_id": None,
        "revoked_by_user_id": None,
        "revoked_reason": None,
        "metadata": {},
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
    }


@pytest.fixture()
def entitlements_list_payload(sample_entitlement: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "success": True,
        "data": {
            "entitlements": [sample_entitlement],
            "count": 1,
        },
        "metadata": {
            "timestamp": "2025-01-09T10:30:00Z",
            "request_id": "req_123",
        },
    }


@pytest.fixture()
def check_payload() -> Dict[str, Any]:
    return {
        "success": True,
        "data": {
            "has_entitlement": True,
            "user_id": "user_456",
            "entitlement_key": "premium_access",
        },
        "metadata": {
            "timestamp": "2025-01-09T10:30:00Z",
            "request_id": "req_123",
        },
    }


@pytest.fixture()
def changes_payload() -> Dict[str, Any]:
    return {
        "success": True,
        "data": {
            "events": [
                {
                    "id": "evt_abc",
                    "entitlement_id": "ent_abc123",
                    "event_type": "granted",
                    "application_id": "app_123",
                    "user_id": "user_456",
                    "email": None,
                    "entitlement_key": "premium_access",
                    "source": "stripe_subscription",
                    "previous_state": None,
                    "new_state": {"active": True},
                    "triggered_by": "webhook",
                    "metadata": {},
                    "created_at": "2025-01-01T00:00:00Z",
                }
            ],
            "cursor": "2025-01-01T00:00:00Z",
            "has_more": False,
        },
        "metadata": {
            "timestamp": "2025-01-09T10:30:00Z",
            "request_id": "req_123",
        },
    }


@pytest.fixture()
def history_payload() -> Dict[str, Any]:
    return {
        "success": True,
        "data": {
            "history": [
                {
                    "id": "ent_abc123",
                    "entitlement_key": "premium_access",
                    "source": "stripe_subscription",
                    "status": "active",
                    "purchased_at": "2025-01-01T00:00:00Z",
                    "starts_at": "2025-01-01T00:00:00Z",
                    "ends_at": "2025-02-01T00:00:00Z",
                    "amount": 29.99,
                    "currency": "usd",
                    "stripe_subscription_id": "sub_xyz",
                    "product_name": "Premium Plan",
                }
            ],
            "count": 1,
        },
        "metadata": {
            "timestamp": "2025-01-09T10:30:00Z",
            "request_id": "req_123",
        },
    }


class TestEntitlementsClient:
    """Tests for EntitlementsClient."""

    @respx.mock
    def test_get_user_entitlements_by_user_id(
        self,
        base_url: str,
        entitlements_client: EntitlementsClient,
        entitlements_list_payload: Dict[str, Any],
    ) -> None:
        """Test getting entitlements by user_id."""
        route = respx.get(f"{base_url}/api/entitlements").mock(
            return_value=Response(200, json=entitlements_list_payload)
        )

        result = entitlements_client.get_user_entitlements(user_id="user_456")

        assert route.called
        assert len(result) == 1
        assert isinstance(result[0], Entitlement)
        assert result[0].id == "ent_abc123"
        assert result[0].entitlement_key == "premium_access"

    @respx.mock
    def test_get_user_entitlements_by_email(
        self,
        base_url: str,
        entitlements_client: EntitlementsClient,
        entitlements_list_payload: Dict[str, Any],
    ) -> None:
        """Test getting entitlements by email."""
        route = respx.get(f"{base_url}/api/entitlements").mock(
            return_value=Response(200, json=entitlements_list_payload)
        )

        result = entitlements_client.get_user_entitlements(email="test@example.com")

        assert route.called
        assert len(result) == 1

    def test_get_user_entitlements_requires_user_or_email(
        self,
        entitlements_client: EntitlementsClient,
    ) -> None:
        """Test that either user_id or email is required."""
        with pytest.raises(ValueError, match="Either user_id or email is required"):
            entitlements_client.get_user_entitlements()

    @respx.mock
    def test_check_access_returns_true(
        self,
        base_url: str,
        entitlements_client: EntitlementsClient,
        check_payload: Dict[str, Any],
    ) -> None:
        """Test quick access check returns True."""
        route = respx.get(f"{base_url}/api/entitlements/check").mock(
            return_value=Response(200, json=check_payload)
        )

        result = entitlements_client.check_access("user_456", "premium_access")

        assert route.called
        assert result is True

    @respx.mock
    def test_check_access_returns_false(
        self,
        base_url: str,
        entitlements_client: EntitlementsClient,
    ) -> None:
        """Test quick access check returns False."""
        payload = {
            "success": True,
            "data": {
                "has_entitlement": False,
                "user_id": "user_456",
                "entitlement_key": "premium_access",
            },
        }
        route = respx.get(f"{base_url}/api/entitlements/check").mock(
            return_value=Response(200, json=payload)
        )

        result = entitlements_client.check_access("user_456", "premium_access")

        assert route.called
        assert result is False

    @respx.mock
    def test_get_changes(
        self,
        base_url: str,
        entitlements_client: EntitlementsClient,
        changes_payload: Dict[str, Any],
    ) -> None:
        """Test getting entitlement changes."""
        route = respx.get(f"{base_url}/api/entitlements/changes").mock(
            return_value=Response(200, json=changes_payload)
        )

        result = entitlements_client.get_changes(since="2025-01-01T00:00:00Z", limit=50)

        assert route.called
        assert isinstance(result, EntitlementChangesResponse)
        assert len(result.events) == 1
        assert result.events[0].event_type == "granted"
        assert result.cursor == "2025-01-01T00:00:00Z"
        assert result.has_more is False

    @respx.mock
    def test_get_purchase_history(
        self,
        base_url: str,
        entitlements_client: EntitlementsClient,
        history_payload: Dict[str, Any],
    ) -> None:
        """Test getting purchase history."""
        route = respx.get(f"{base_url}/api/entitlements/history").mock(
            return_value=Response(200, json=history_payload)
        )

        result = entitlements_client.get_purchase_history("user_456")

        assert route.called
        assert len(result) == 1
        assert isinstance(result[0], PurchaseHistoryItem)
        assert result[0].amount == 29.99
        assert result[0].status == "active"

    @respx.mock
    def test_claim_pending(
        self,
        base_url: str,
        entitlements_client: EntitlementsClient,
        sample_entitlement: Dict[str, Any],
    ) -> None:
        """Test claiming pending entitlements."""
        payload = {
            "success": True,
            "data": {
                "claimed": [sample_entitlement],
                "count": 1,
            },
        }
        route = respx.post(f"{base_url}/api/entitlements/claim").mock(
            return_value=Response(200, json=payload)
        )

        result = entitlements_client.claim_pending()

        assert route.called
        assert result.count == 1
        assert len(result.claimed) == 1

    def test_claim_pending_requires_token(
        self,
        base_url: str,
        api_key: str,
    ) -> None:
        """Test that claim requires access token."""
        client = EntitlementsClient(base_url=base_url, api_key=api_key)
        with pytest.raises(ValueError, match="Access token is required"):
            client.claim_pending()

    @respx.mock
    def test_grant_manual(
        self,
        base_url: str,
        entitlements_client: EntitlementsClient,
        sample_entitlement: Dict[str, Any],
    ) -> None:
        """Test granting manual entitlement."""
        # Update sample to be manual source
        sample_entitlement["source"] = "manual"
        sample_entitlement["manual_grant_reason"] = "Test grant"
        payload = {
            "success": True,
            "data": {
                "entitlement": sample_entitlement,
            },
        }
        route = respx.post(f"{base_url}/api/entitlements/manual").mock(
            return_value=Response(201, json=payload)
        )

        params = ManualGrantParams(
            entitlement_key="premium_access",
            beneficiary_user_id="user_456",
            reason="Test grant",
        )
        result = entitlements_client.grant_manual(params)

        assert route.called
        assert isinstance(result, Entitlement)
        assert result.source == "manual"

    @respx.mock
    def test_revoke(
        self,
        base_url: str,
        entitlements_client: EntitlementsClient,
        sample_entitlement: Dict[str, Any],
    ) -> None:
        """Test revoking entitlement."""
        sample_entitlement["revoked_at"] = "2025-01-09T10:30:00Z"
        sample_entitlement["revoked_reason"] = "User requested"
        payload = {
            "success": True,
            "data": {
                "entitlement": sample_entitlement,
            },
        }
        route = respx.delete(f"{base_url}/api/entitlements/ent_abc123").mock(
            return_value=Response(200, json=payload)
        )

        result = entitlements_client.revoke("ent_abc123", reason="User requested")

        assert route.called
        assert isinstance(result, Entitlement)
        assert result.revoked_at is not None

    @respx.mock
    def test_error_handling(
        self,
        base_url: str,
        entitlements_client: EntitlementsClient,
    ) -> None:
        """Test error response handling."""
        error_payload = {
            "success": False,
            "error": {
                "code": "NOT_FOUND",
                "message": "Entitlement not found",
            },
            "metadata": {
                "request_id": "req_123",
            },
        }
        respx.get(f"{base_url}/api/entitlements").mock(
            return_value=Response(404, json=error_payload)
        )

        with pytest.raises(EntitlementsError) as exc_info:
            entitlements_client.get_user_entitlements(user_id="user_456")

        assert exc_info.value.status_code == 404
        assert exc_info.value.error_code == "NOT_FOUND"
        assert exc_info.value.request_id == "req_123"
