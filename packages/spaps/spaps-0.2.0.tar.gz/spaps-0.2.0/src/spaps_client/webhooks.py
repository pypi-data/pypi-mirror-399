"""
SPAPS Webhook verification helpers.

Provides signature verification for incoming SPAPS webhooks using
the unified signature format: t=<timestamp>,v1=<hmac_sha256_hex>
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
import time
from dataclasses import field
from typing import Any, Dict, Literal, Optional, Union

from pydantic import BaseModel


class WebhookVerificationError(Exception):
    """Raised when webhook signature verification fails."""

    def __init__(self, message: str, code: Optional[str] = None) -> None:
        super().__init__(message)
        self.code = code


class SpapsWebhookPayload(BaseModel):
    """Unified webhook payload envelope from SPAPS."""

    id: str
    type: str
    schema_version: int
    application_id: str
    created_at: str
    data: Dict[str, Any]


# --------------------
# Entitlement Event Types
# --------------------


class EntitlementEventData(BaseModel):
    """Common data for entitlement events."""

    entitlement_id: str
    user_id: Optional[str] = None
    email: Optional[str] = None
    entitlement_key: str
    source: Literal["crypto", "stripe_subscription", "stripe_checkout", "manual"]
    starts_at: str
    ends_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class EntitlementGrantedEvent(BaseModel):
    """Payload for entitlement.granted webhook events."""

    id: str
    type: Literal["entitlement.granted"]
    schema_version: int
    application_id: str
    created_at: str
    data: EntitlementEventData


class EntitlementRenewedEvent(BaseModel):
    """Payload for entitlement.renewed webhook events."""

    id: str
    type: Literal["entitlement.renewed"]
    schema_version: int
    application_id: str
    created_at: str
    data: EntitlementEventData


class EntitlementUpdatedEvent(BaseModel):
    """Payload for entitlement.updated webhook events."""

    id: str
    type: Literal["entitlement.updated"]
    schema_version: int
    application_id: str
    created_at: str
    data: EntitlementEventData


class EntitlementExpiredEvent(BaseModel):
    """Payload for entitlement.expired webhook events."""

    id: str
    type: Literal["entitlement.expired"]
    schema_version: int
    application_id: str
    created_at: str
    data: EntitlementEventData


class EntitlementRevokedEvent(BaseModel):
    """Payload for entitlement.revoked webhook events."""

    id: str
    type: Literal["entitlement.revoked"]
    schema_version: int
    application_id: str
    created_at: str
    data: EntitlementEventData


class EntitlementClaimedEvent(BaseModel):
    """Payload for entitlement.claimed webhook events."""

    id: str
    type: Literal["entitlement.claimed"]
    schema_version: int
    application_id: str
    created_at: str
    data: EntitlementEventData


# Union type for all entitlement events
EntitlementEvent = Union[
    EntitlementGrantedEvent,
    EntitlementRenewedEvent,
    EntitlementUpdatedEvent,
    EntitlementExpiredEvent,
    EntitlementRevokedEvent,
    EntitlementClaimedEvent,
]


# --------------------
# Signature Verification
# --------------------


# Pattern for unified signature format: t=<timestamp>,v1=<hex>
SIGNATURE_PATTERN = re.compile(r"^t=(\d+),v1=([a-f0-9]{64})$")

# Default signature expiry: 5 minutes
DEFAULT_MAX_AGE_SECONDS = 300


def verify_spaps_webhook(
    body: Union[bytes, str],
    signature: str,
    secret: str,
    *,
    max_age_seconds: int = DEFAULT_MAX_AGE_SECONDS,
    timestamp: Optional[int] = None,
) -> SpapsWebhookPayload:
    """
    Verify a SPAPS webhook signature and return the parsed payload.

    Signature format: t=<unix_timestamp>,v1=<hmac_sha256_hex>
    HMAC is computed on: <timestamp>.<json_body>

    Args:
        body: Raw request body (bytes or string)
        signature: Value of X-SPAPS-Signature header
        secret: Webhook secret from SPAPS
        max_age_seconds: Maximum age of signature (default 5 minutes)
        timestamp: Override current time for testing

    Returns:
        SpapsWebhookPayload with parsed event data

    Raises:
        WebhookVerificationError: If signature is invalid or expired
    """
    # Ensure body is a string for signature computation
    if isinstance(body, bytes):
        body_str = body.decode("utf-8")
    else:
        body_str = body

    # Parse signature format
    match = SIGNATURE_PATTERN.match(signature)
    if not match:
        raise WebhookVerificationError(
            "Invalid signature format. Expected t=<timestamp>,v1=<hmac>",
            code="INVALID_FORMAT",
        )

    sig_timestamp = int(match.group(1))
    provided_hmac = match.group(2)

    # Check timestamp age
    current_time = timestamp if timestamp is not None else int(time.time())
    age = current_time - sig_timestamp

    if age < 0:
        raise WebhookVerificationError(
            f"Signature timestamp is in the future by {-age} seconds",
            code="TIMESTAMP_FUTURE",
        )

    if age > max_age_seconds:
        raise WebhookVerificationError(
            f"Signature expired. Age: {age}s, max allowed: {max_age_seconds}s",
            code="SIGNATURE_EXPIRED",
        )

    # Compute expected HMAC
    signature_base = f"{sig_timestamp}.{body_str}"
    expected_hmac = hmac.new(
        secret.encode("utf-8"),
        signature_base.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    # Constant-time comparison
    if not hmac.compare_digest(expected_hmac, provided_hmac):
        raise WebhookVerificationError(
            "Signature verification failed",
            code="INVALID_SIGNATURE",
        )

    # Parse and return payload
    try:
        payload = json.loads(body_str)
    except json.JSONDecodeError as e:
        raise WebhookVerificationError(
            f"Invalid JSON payload: {e}",
            code="INVALID_JSON",
        )

    return SpapsWebhookPayload.model_validate(payload)


def parse_entitlement_event(payload: SpapsWebhookPayload) -> Optional[EntitlementEvent]:
    """
    Parse a webhook payload into a typed entitlement event.

    Args:
        payload: Verified SpapsWebhookPayload

    Returns:
        Typed entitlement event, or None if not an entitlement event
    """
    payload_dict = payload.model_dump()

    if payload.type == "entitlement.granted":
        return EntitlementGrantedEvent.model_validate(payload_dict)
    elif payload.type == "entitlement.renewed":
        return EntitlementRenewedEvent.model_validate(payload_dict)
    elif payload.type == "entitlement.updated":
        return EntitlementUpdatedEvent.model_validate(payload_dict)
    elif payload.type == "entitlement.expired":
        return EntitlementExpiredEvent.model_validate(payload_dict)
    elif payload.type == "entitlement.revoked":
        return EntitlementRevokedEvent.model_validate(payload_dict)
    elif payload.type == "entitlement.claimed":
        return EntitlementClaimedEvent.model_validate(payload_dict)

    return None


def generate_test_signature(
    payload: Dict[str, Any],
    secret: str,
    timestamp: Optional[int] = None,
) -> str:
    """
    Generate a SPAPS webhook signature for testing.

    Args:
        payload: Webhook payload dictionary
        secret: Webhook secret
        timestamp: Unix timestamp (default: current time)

    Returns:
        Signature string in format: t=<timestamp>,v1=<hmac>
    """
    ts = timestamp if timestamp is not None else int(time.time())
    payload_str = json.dumps(payload)
    signature_base = f"{ts}.{payload_str}"
    hmac_hex = hmac.new(
        secret.encode("utf-8"),
        signature_base.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"t={ts},v1={hmac_hex}"


__all__ = [
    "WebhookVerificationError",
    "SpapsWebhookPayload",
    "EntitlementEventData",
    "EntitlementGrantedEvent",
    "EntitlementRenewedEvent",
    "EntitlementUpdatedEvent",
    "EntitlementExpiredEvent",
    "EntitlementRevokedEvent",
    "EntitlementClaimedEvent",
    "EntitlementEvent",
    "verify_spaps_webhook",
    "parse_entitlement_event",
    "generate_test_signature",
    "DEFAULT_MAX_AGE_SECONDS",
]
