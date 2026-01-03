"""Async entitlements client mirroring the synchronous EntitlementsClient API."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from .entitlements import (
    EntitlementsError,
    Entitlement,
    EntitlementChangesResponse,
    EntitlementCheckResponse,
    EntitlementClaimResponse,
    EntitlementGrantResponse,
    EntitlementRevokeResponse,
    EntitlementsListResponse,
    ManualGrantParams,
    PurchaseHistoryItem,
    PurchaseHistoryResponse,
)


class AsyncEntitlementsClient:
    """Async client for the entitlements API."""

    ENTITLEMENTS_PREFIX = "/api/entitlements"

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        access_token: Optional[str] = None,
        client: Optional[httpx.AsyncClient] = None,
        request_timeout: float | httpx.Timeout = 10.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.access_token = access_token
        self._client = client or httpx.AsyncClient(base_url=self.base_url, timeout=request_timeout)
        self._owns_client = client is None

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def get_user_entitlements(
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

        data = await self._get("", params=params)
        response = EntitlementsListResponse.model_validate(data)
        return response.entitlements

    async def check_access(
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
        data = await self._get("/check", params=params)
        response = EntitlementCheckResponse.model_validate(data)
        return response.has_entitlement

    async def get_changes(
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

        data = await self._get("/changes", params=params)
        return EntitlementChangesResponse.model_validate(data)

    async def get_purchase_history(
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
        data = await self._get("/history", params=params)
        response = PurchaseHistoryResponse.model_validate(data)
        return response.history

    async def claim_pending(
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

        response = await self._client.post(
            f"{self.ENTITLEMENTS_PREFIX}/claim",
            headers=headers,
            json={},
        )
        data = await self._parse_response(response)
        return EntitlementClaimResponse.model_validate(data)

    async def grant_manual(
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

        response = await self._client.post(
            f"{self.ENTITLEMENTS_PREFIX}/manual",
            headers=headers,
            json=payload,
        )
        data = await self._parse_response(response)
        result = EntitlementGrantResponse.model_validate(data)
        return result.entitlement

    async def revoke(
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

        response = await self._client.request(
            "DELETE",
            f"{self.ENTITLEMENTS_PREFIX}/{entitlement_id}",
            headers=headers,
            json=payload,
        )
        data = await self._parse_response(response)
        result = EntitlementRevokeResponse.model_validate(data)
        return result.entitlement

    async def _get(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        response = await self._client.get(
            f"{self.ENTITLEMENTS_PREFIX}{path}",
            headers=self._build_headers(),
            params=params,
        )
        return await self._parse_response(response)

    def _build_headers(self) -> Dict[str, str]:
        return {"X-API-Key": self.api_key}

    async def _parse_response(self, response: httpx.Response) -> Dict[str, Any]:
        if response.status_code >= 400:
            raise await self._build_error(response)
        payload = response.json()
        return payload.get("data", payload)

    @staticmethod
    async def _build_error(response: httpx.Response) -> EntitlementsError:
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


__all__ = ["AsyncEntitlementsClient"]
