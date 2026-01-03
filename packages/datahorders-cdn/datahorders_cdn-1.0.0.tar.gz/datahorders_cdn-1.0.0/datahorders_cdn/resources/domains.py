"""Domains resource for the DataHorders CDN SDK."""

from __future__ import annotations

import builtins
from typing import Any

from datahorders_cdn.models import (
    Domain,
    DomainCreateResponse,
    DomainDeleteResponse,
    DomainVerifyResponse,
    PaginationMeta,
)
from datahorders_cdn.resources.base import BaseResource

# Alias to avoid shadowing by the `list` method in classes
_list = builtins.list


class DomainsResource(BaseResource):
    """Resource for managing domains.

    Domains must be registered and verified before they can be used in zones.
    """

    def list(
        self,
        page: int = 1,
        per_page: int = 10,
        verified: bool | None = None,
    ) -> tuple[_list[Domain], PaginationMeta]:
        """List all domains.

        Args:
            page: Page number (1-indexed).
            per_page: Items per page.
            verified: Filter by verification status.

        Returns:
            Tuple of (list of domains, pagination metadata).
        """
        params: dict[str, Any] = {"page": page, "perPage": per_page}
        if verified is not None:
            params["verified"] = str(verified).lower()

        response = self._get("/domains", params=params)
        domains = [Domain.model_validate(d) for d in response.get("data", [])]
        meta = PaginationMeta.model_validate(response.get("meta", {}))
        return domains, meta

    async def list_async(
        self,
        page: int = 1,
        per_page: int = 10,
        verified: bool | None = None,
    ) -> tuple[_list[Domain], PaginationMeta]:
        """List all domains asynchronously.

        Args:
            page: Page number (1-indexed).
            per_page: Items per page.
            verified: Filter by verification status.

        Returns:
            Tuple of (list of domains, pagination metadata).
        """
        params: dict[str, Any] = {"page": page, "perPage": per_page}
        if verified is not None:
            params["verified"] = str(verified).lower()

        response = await self._get_async("/domains", params=params)
        domains = [Domain.model_validate(d) for d in response.get("data", [])]
        meta = PaginationMeta.model_validate(response.get("meta", {}))
        return domains, meta

    def get(self, domain_id: str) -> Domain:
        """Get a specific domain by ID.

        Args:
            domain_id: The domain ID.

        Returns:
            The domain object.
        """
        response = self._get("/domains", params={"id": domain_id})
        return Domain.model_validate(response.get("data", {}))

    async def get_async(self, domain_id: str) -> Domain:
        """Get a specific domain by ID asynchronously.

        Args:
            domain_id: The domain ID.

        Returns:
            The domain object.
        """
        response = await self._get_async("/domains", params={"id": domain_id})
        return Domain.model_validate(response.get("data", {}))

    def create(
        self,
        domain: str,
        health_check_enabled: bool = False,
    ) -> DomainCreateResponse:
        """Register a new domain.

        The domain will be created in an unverified state with instructions
        for DNS verification.

        Args:
            domain: Domain name to register (no wildcards).
            health_check_enabled: Enable health checks for this domain.

        Returns:
            Domain creation response with verification instructions.
        """
        data = {
            "domain": domain,
            "healthCheckEnabled": health_check_enabled,
        }
        response = self._post("/domains", data=data)
        return DomainCreateResponse.model_validate(response.get("data", {}))

    async def create_async(
        self,
        domain: str,
        health_check_enabled: bool = False,
    ) -> DomainCreateResponse:
        """Register a new domain asynchronously.

        The domain will be created in an unverified state with instructions
        for DNS verification.

        Args:
            domain: Domain name to register (no wildcards).
            health_check_enabled: Enable health checks for this domain.

        Returns:
            Domain creation response with verification instructions.
        """
        data = {
            "domain": domain,
            "healthCheckEnabled": health_check_enabled,
        }
        response = await self._post_async("/domains", data=data)
        return DomainCreateResponse.model_validate(response.get("data", {}))

    def delete(self, domain_id: str) -> DomainDeleteResponse:
        """Delete a domain.

        The domain cannot be deleted if it is used in any zones.

        Args:
            domain_id: The domain ID to delete.

        Returns:
            Deletion confirmation.
        """
        response = self._delete("/domains", params={"id": domain_id})
        return DomainDeleteResponse.model_validate(response.get("data", {}))

    async def delete_async(self, domain_id: str) -> DomainDeleteResponse:
        """Delete a domain asynchronously.

        The domain cannot be deleted if it is used in any zones.

        Args:
            domain_id: The domain ID to delete.

        Returns:
            Deletion confirmation.
        """
        response = await self._delete_async("/domains", params={"id": domain_id})
        return DomainDeleteResponse.model_validate(response.get("data", {}))

    def verify(
        self,
        domain: str | None = None,
        domain_id: str | None = None,
    ) -> DomainVerifyResponse:
        """Verify domain ownership.

        Checks for the DNS TXT record to verify domain ownership.
        Provide either domain name or domain ID.

        Args:
            domain: Domain name to verify.
            domain_id: Domain ID to verify.

        Returns:
            Verification result.

        Raises:
            ValueError: If neither domain nor domain_id is provided.
        """
        if not domain and not domain_id:
            raise ValueError("Either domain or domain_id must be provided")

        data: dict[str, str] = {}
        if domain:
            data["domain"] = domain
        if domain_id:
            data["id"] = domain_id

        response = self._post("/domains/verify", data=data)
        return DomainVerifyResponse.model_validate(response.get("data", {}))

    async def verify_async(
        self,
        domain: str | None = None,
        domain_id: str | None = None,
    ) -> DomainVerifyResponse:
        """Verify domain ownership asynchronously.

        Checks for the DNS TXT record to verify domain ownership.
        Provide either domain name or domain ID.

        Args:
            domain: Domain name to verify.
            domain_id: Domain ID to verify.

        Returns:
            Verification result.

        Raises:
            ValueError: If neither domain nor domain_id is provided.
        """
        if not domain and not domain_id:
            raise ValueError("Either domain or domain_id must be provided")

        data: dict[str, str] = {}
        if domain:
            data["domain"] = domain
        if domain_id:
            data["id"] = domain_id

        response = await self._post_async("/domains/verify", data=data)
        return DomainVerifyResponse.model_validate(response.get("data", {}))
