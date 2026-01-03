"""
Entitlements client for SPAPS.

Provides access to entitlement queries, checks, claims, and admin operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional

import httpx
from pydantic import BaseModel


class EntitlementsError(Exception):
    """Error from the entitlements API."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        response: Optional[httpx.Response] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.response = response
        self.request_id = request_id


# --------------------
# Response Models
# --------------------


class Entitlement(BaseModel):
    """An entitlement record."""

    id: str
    application_id: str
    beneficiary_user_id: Optional[str] = None
    beneficiary_email: Optional[str] = None
    entitlement_key: str
    source: Literal["crypto", "stripe_subscription", "stripe_checkout", "manual"]

    # Timing
    starts_at: str
    ends_at: Optional[str] = None
    revoked_at: Optional[str] = None

    # Source-specific references
    crypto_invoice_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    stripe_session_id: Optional[str] = None
    stripe_invoice_id: Optional[str] = None
    stripe_product_id: Optional[str] = None

    # Manual grant fields
    manual_grant_id: Optional[str] = None
    manual_grant_reason: Optional[str] = None
    granted_by_user_id: Optional[str] = None

    # Revocation
    revoked_by_user_id: Optional[str] = None
    revoked_reason: Optional[str] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str
    updated_at: Optional[str] = None


class EntitlementEvent(BaseModel):
    """An entitlement change event for sync/audit."""

    id: str
    entitlement_id: str
    event_type: Literal["granted", "updated", "renewed", "expired", "revoked", "claimed"]
    application_id: str
    user_id: Optional[str] = None
    email: Optional[str] = None
    entitlement_key: str
    source: Literal["crypto", "stripe_subscription", "stripe_checkout", "manual"]
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    triggered_by: Optional[Literal["webhook", "api", "cron", "claim"]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str


class EntitlementsListResponse(BaseModel):
    """Response from GET /api/entitlements."""

    entitlements: List[Entitlement]
    count: int


class EntitlementCheckResponse(BaseModel):
    """Response from GET /api/entitlements/check."""

    has_entitlement: bool
    user_id: str
    entitlement_key: str


class EntitlementChangesResponse(BaseModel):
    """Response from GET /api/entitlements/changes."""

    events: List[EntitlementEvent]
    cursor: Optional[str] = None
    has_more: bool = False


class EntitlementClaimResponse(BaseModel):
    """Response from POST /api/entitlements/claim."""

    claimed: List[Entitlement]
    count: int


class PurchaseHistoryItem(BaseModel):
    """A purchase history item."""

    id: str
    entitlement_key: str
    source: Literal["crypto", "stripe_subscription", "stripe_checkout", "manual"]
    status: Literal["active", "expired", "canceled", "revoked"]

    # Timing
    purchased_at: str
    starts_at: str
    ends_at: Optional[str] = None

    # Payment details
    amount: Optional[float] = None
    currency: Optional[str] = None
    stripe_invoice_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    crypto_invoice_id: Optional[str] = None

    # Display
    product_name: Optional[str] = None


class PurchaseHistoryResponse(BaseModel):
    """Response from GET /api/entitlements/history."""

    history: List[PurchaseHistoryItem]
    count: int


class EntitlementGrantResponse(BaseModel):
    """Response from POST /api/entitlements/manual."""

    entitlement: Entitlement


class EntitlementRevokeResponse(BaseModel):
    """Response from DELETE /api/entitlements/:id."""

    entitlement: Entitlement


# --------------------
# Request Models
# --------------------


@dataclass
class ManualGrantParams:
    """Parameters for granting a manual entitlement."""

    entitlement_key: str
    beneficiary_user_id: Optional[str] = None
    beneficiary_email: Optional[str] = None
    starts_at: Optional[str] = None
    ends_at: Optional[str] = None
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# --------------------
# Synchronous Client
# --------------------


class EntitlementsClient:
    """Synchronous client for the entitlements API."""

    ENTITLEMENTS_PREFIX = "/api/entitlements"

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        access_token: Optional[str] = None,
        client: Optional[httpx.Client] = None,
        request_timeout: float = 10.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.access_token = access_token
        self._client = client or httpx.Client(base_url=self.base_url, timeout=request_timeout)
        self._owns_client = client is None

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def get_user_entitlements(
        self,
        *,
        user_id: Optional[str] = None,
        email: Optional[str] = None,
        entitlement_key: Optional[str] = None,
        include_expired: bool = False,
        include_revoked: bool = False,
        limit: Optional[int] = None,
    ) -> List[Entitlement]:
        """
        Get entitlements for a user by user_id or email.

        Args:
            user_id: The user's UUID
            email: The user's email address
            entitlement_key: Filter by specific entitlement key
            include_expired: Include expired entitlements
            include_revoked: Include revoked entitlements
            limit: Maximum number of results

        Returns:
            List of Entitlement objects
        """
        if not user_id and not email:
            raise ValueError("Either user_id or email is required")

        params: Dict[str, Any] = {}
        if user_id:
            params["user_id"] = user_id
        if email:
            params["email"] = email
        if entitlement_key:
            params["entitlement_key"] = entitlement_key
        if include_expired:
            params["include_expired"] = "true"
        if include_revoked:
            params["include_revoked"] = "true"
        if limit:
            params["limit"] = str(limit)

        data = self._get("", params=params)
        response = EntitlementsListResponse.model_validate(data)
        return response.entitlements

    def check_access(
        self,
        user_id: str,
        entitlement_key: str,
    ) -> bool:
        """
        Quick boolean check if user has a specific entitlement.

        Args:
            user_id: The user's UUID
            entitlement_key: The entitlement key to check

        Returns:
            True if user has valid entitlement, False otherwise
        """
        params = {"user_id": user_id, "key": entitlement_key}
        data = self._get("/check", params=params)
        response = EntitlementCheckResponse.model_validate(data)
        return response.has_entitlement

    def get_changes(
        self,
        *,
        since: Optional[str] = None,
        limit: int = 100,
    ) -> EntitlementChangesResponse:
        """
        Get entitlement changes for syncing.

        Args:
            since: ISO timestamp to get changes since (cursor from previous call)
            limit: Maximum number of events to return

        Returns:
            EntitlementChangesResponse with events and cursor
        """
        params: Dict[str, Any] = {"limit": str(limit)}
        if since:
            params["since"] = since

        data = self._get("/changes", params=params)
        return EntitlementChangesResponse.model_validate(data)

    def get_purchase_history(
        self,
        user_id: str,
    ) -> List[PurchaseHistoryItem]:
        """
        Get purchase/payment history for a user.

        Args:
            user_id: The user's UUID

        Returns:
            List of PurchaseHistoryItem objects
        """
        params = {"user_id": user_id}
        data = self._get("/history", params=params)
        response = PurchaseHistoryResponse.model_validate(data)
        return response.history

    def claim_pending(
        self,
        *,
        access_token: Optional[str] = None,
    ) -> EntitlementClaimResponse:
        """
        Claim pending entitlements for the authenticated user.

        This endpoint requires JWT authentication and will claim
        entitlements matching the user's verified email.

        Args:
            access_token: JWT access token (overrides stored token)

        Returns:
            EntitlementClaimResponse with claimed entitlements
        """
        token = access_token or self.access_token
        if not token:
            raise ValueError("Access token is required for claim operation")

        headers = self._build_headers()
        headers["Authorization"] = f"Bearer {token}"

        response = self._client.post(
            f"{self.ENTITLEMENTS_PREFIX}/claim",
            headers=headers,
            json={},
        )
        data = self._parse_response(response)
        return EntitlementClaimResponse.model_validate(data)

    def grant_manual(
        self,
        params: ManualGrantParams,
        *,
        access_token: Optional[str] = None,
    ) -> Entitlement:
        """
        Admin: Grant a manual entitlement.

        Requires admin JWT authentication.

        Args:
            params: ManualGrantParams with entitlement details
            access_token: Admin JWT access token

        Returns:
            The created Entitlement
        """
        token = access_token or self.access_token
        if not token:
            raise ValueError("Access token is required for admin operations")

        headers = self._build_headers()
        headers["Authorization"] = f"Bearer {token}"

        payload: Dict[str, Any] = {"entitlement_key": params.entitlement_key}
        if params.beneficiary_user_id:
            payload["beneficiary_user_id"] = params.beneficiary_user_id
        if params.beneficiary_email:
            payload["beneficiary_email"] = params.beneficiary_email
        if params.starts_at:
            payload["starts_at"] = params.starts_at
        if params.ends_at:
            payload["ends_at"] = params.ends_at
        if params.reason:
            payload["reason"] = params.reason
        if params.metadata:
            payload["metadata"] = params.metadata

        response = self._client.post(
            f"{self.ENTITLEMENTS_PREFIX}/manual",
            headers=headers,
            json=payload,
        )
        data = self._parse_response(response)
        result = EntitlementGrantResponse.model_validate(data)
        return result.entitlement

    def revoke(
        self,
        entitlement_id: str,
        *,
        reason: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> Entitlement:
        """
        Admin: Revoke an entitlement.

        Requires admin JWT authentication.

        Args:
            entitlement_id: The entitlement UUID to revoke
            reason: Optional reason for revocation
            access_token: Admin JWT access token

        Returns:
            The revoked Entitlement
        """
        token = access_token or self.access_token
        if not token:
            raise ValueError("Access token is required for admin operations")

        headers = self._build_headers()
        headers["Authorization"] = f"Bearer {token}"

        payload: Dict[str, Any] = {}
        if reason:
            payload["reason"] = reason

        response = self._client.request(
            "DELETE",
            f"{self.ENTITLEMENTS_PREFIX}/{entitlement_id}",
            headers=headers,
            json=payload,
        )
        data = self._parse_response(response)
        result = EntitlementRevokeResponse.model_validate(data)
        return result.entitlement

    def _get(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        response = self._client.get(
            f"{self.ENTITLEMENTS_PREFIX}{path}",
            headers=self._build_headers(),
            params=params,
        )
        return self._parse_response(response)

    def _build_headers(self) -> Dict[str, str]:
        return {"X-API-Key": self.api_key}

    def _parse_response(self, response: httpx.Response) -> Dict[str, Any]:
        if response.status_code >= 400:
            raise self._build_error(response)
        payload = response.json()
        return payload.get("data", payload)

    @staticmethod
    def _build_error(response: httpx.Response) -> EntitlementsError:
        try:
            payload = response.json()
        except ValueError:
            payload = {}
        error_info = payload.get("error", {})
        message = error_info.get("message") or response.text or "Entitlements request failed"
        request_id = (
            response.headers.get("x-request-id")
            or payload.get("metadata", {}).get("request_id")
        )
        return EntitlementsError(
            message,
            status_code=response.status_code,
            error_code=error_info.get("code"),
            response=response,
            request_id=request_id,
        )


__all__ = [
    "EntitlementsClient",
    "EntitlementsError",
    "Entitlement",
    "EntitlementEvent",
    "EntitlementsListResponse",
    "EntitlementCheckResponse",
    "EntitlementChangesResponse",
    "EntitlementClaimResponse",
    "PurchaseHistoryItem",
    "PurchaseHistoryResponse",
    "EntitlementGrantResponse",
    "EntitlementRevokeResponse",
    "ManualGrantParams",
]
