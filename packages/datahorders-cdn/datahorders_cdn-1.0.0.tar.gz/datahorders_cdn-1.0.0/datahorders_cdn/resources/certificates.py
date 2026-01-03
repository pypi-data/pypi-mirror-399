"""Certificates resource for the DataHorders CDN SDK."""

from __future__ import annotations

import builtins
from typing import Any

from datahorders_cdn.models import (
    AcmeCertificateStatus,
    AcmeProvider,
    Certificate,
    CertificateDeleteResponse,
    PaginationMeta,
)
from datahorders_cdn.resources.base import BaseResource

# Alias to avoid shadowing by the `list` method in classes
_list = builtins.list


class CertificatesResource(BaseResource):
    """Resource for managing SSL/TLS certificates.

    Supports both manual certificate uploads and automated ACME certificates.
    """

    def list(
        self,
        page: int = 1,
        per_page: int = 10,
        status: str | None = None,
    ) -> tuple[_list[Certificate], PaginationMeta]:
        """List all certificates.

        Args:
            page: Page number (1-indexed).
            per_page: Items per page.
            status: Filter by status ('active', 'pending', 'failed', 'expired').

        Returns:
            Tuple of (list of certificates, pagination metadata).
        """
        params: dict[str, Any] = {"page": page, "perPage": per_page}
        if status:
            params["status"] = status

        response = self._get("/certificates", params=params)
        certs = [Certificate.model_validate(c) for c in response.get("data", [])]
        meta = PaginationMeta.model_validate(response.get("meta", {}))
        return certs, meta

    async def list_async(
        self,
        page: int = 1,
        per_page: int = 10,
        status: str | None = None,
    ) -> tuple[_list[Certificate], PaginationMeta]:
        """List all certificates asynchronously.

        Args:
            page: Page number (1-indexed).
            per_page: Items per page.
            status: Filter by status.

        Returns:
            Tuple of (list of certificates, pagination metadata).
        """
        params: dict[str, Any] = {"page": page, "perPage": per_page}
        if status:
            params["status"] = status

        response = await self._get_async("/certificates", params=params)
        certs = [Certificate.model_validate(c) for c in response.get("data", [])]
        meta = PaginationMeta.model_validate(response.get("meta", {}))
        return certs, meta

    def get(
        self,
        domain: str,
        include_sensitive_data: bool = False,
    ) -> Certificate:
        """Get a certificate by domain.

        Args:
            domain: Domain name covered by the certificate.
            include_sensitive_data: Include certificate content.

        Returns:
            The certificate object.
        """
        params: dict[str, Any] = {"domain": domain}
        if include_sensitive_data:
            params["includeSensitiveData"] = "true"

        response = self._get("/certificates", params=params)
        return Certificate.model_validate(response.get("data", response))

    async def get_async(
        self,
        domain: str,
        include_sensitive_data: bool = False,
    ) -> Certificate:
        """Get a certificate by domain asynchronously.

        Args:
            domain: Domain name covered by the certificate.
            include_sensitive_data: Include certificate content.

        Returns:
            The certificate object.
        """
        params: dict[str, Any] = {"domain": domain}
        if include_sensitive_data:
            params["includeSensitiveData"] = "true"

        response = await self._get_async("/certificates", params=params)
        return Certificate.model_validate(response.get("data", response))

    def create(
        self,
        name: str,
        cert_content: str,
        key_content: str,
        domains: _list[str] | None = None,
        auto_renew: bool = False,
        force: bool = False,
    ) -> Certificate:
        """Create a manual certificate.

        Upload your own SSL/TLS certificate and private key.

        Args:
            name: Display name for the certificate.
            cert_content: PEM-encoded certificate (include chain).
            key_content: PEM-encoded private key.
            domains: Domain names (auto-detected from cert if omitted).
            auto_renew: Enable auto-renewal.
            force: Replace existing certificate for domain.

        Returns:
            The created certificate.
        """
        data: dict[str, Any] = {
            "name": name,
            "provider": "manual",
            "certContent": cert_content,
            "keyContent": key_content,
            "autoRenew": auto_renew,
        }
        if domains:
            data["domains"] = domains
        if force:
            data["force"] = True

        response = self._post("/certificates", data=data)
        return Certificate.model_validate(response.get("data", response))

    async def create_async(
        self,
        name: str,
        cert_content: str,
        key_content: str,
        domains: _list[str] | None = None,
        auto_renew: bool = False,
        force: bool = False,
    ) -> Certificate:
        """Create a manual certificate asynchronously.

        Args:
            name: Display name for the certificate.
            cert_content: PEM-encoded certificate (include chain).
            key_content: PEM-encoded private key.
            domains: Domain names (auto-detected from cert if omitted).
            auto_renew: Enable auto-renewal.
            force: Replace existing certificate for domain.

        Returns:
            The created certificate.
        """
        data: dict[str, Any] = {
            "name": name,
            "provider": "manual",
            "certContent": cert_content,
            "keyContent": key_content,
            "autoRenew": auto_renew,
        }
        if domains:
            data["domains"] = domains
        if force:
            data["force"] = True

        response = await self._post_async("/certificates", data=data)
        return Certificate.model_validate(response.get("data", response))

    def create_acme(
        self,
        name: str,
        domains: _list[str],
        email: str,
        acme_provider: AcmeProvider = AcmeProvider.LETSENCRYPT,
        auto_renew: bool = True,
        force: bool = False,
    ) -> AcmeCertificateStatus:
        """Request an ACME certificate.

        Creates a new SSL/TLS certificate using automated ACME validation.
        The certificate is created with 'pending' status and processed
        asynchronously.

        Args:
            name: Display name for the certificate.
            domains: Domain names to include (can include wildcards).
            email: Contact email for ACME account.
            acme_provider: ACME provider ('letsencrypt', 'zerossl', 'google').
            auto_renew: Enable automatic renewal.
            force: Replace existing certificate for domain.

        Returns:
            ACME certificate status (poll to check progress).

        Example:
            >>> status = client.certificates.create_acme(
            ...     name="example.com Wildcard",
            ...     domains=["example.com", "*.example.com"],
            ...     email="admin@example.com",
            ... )
            >>> print(status.certificate_id)
        """
        data: dict[str, Any] = {
            "name": name,
            "domains": domains,
            "email": email,
            "acmeProvider": acme_provider.value,
            "autoRenew": auto_renew,
        }
        if force:
            data["force"] = True

        response = self._post("/certificates/acme", data=data)
        return AcmeCertificateStatus.model_validate(response.get("data", response))

    async def create_acme_async(
        self,
        name: str,
        domains: _list[str],
        email: str,
        acme_provider: AcmeProvider = AcmeProvider.LETSENCRYPT,
        auto_renew: bool = True,
        force: bool = False,
    ) -> AcmeCertificateStatus:
        """Request an ACME certificate asynchronously.

        Args:
            name: Display name for the certificate.
            domains: Domain names to include (can include wildcards).
            email: Contact email for ACME account.
            acme_provider: ACME provider.
            auto_renew: Enable automatic renewal.
            force: Replace existing certificate for domain.

        Returns:
            ACME certificate status.
        """
        data: dict[str, Any] = {
            "name": name,
            "domains": domains,
            "email": email,
            "acmeProvider": acme_provider.value,
            "autoRenew": auto_renew,
        }
        if force:
            data["force"] = True

        response = await self._post_async("/certificates/acme", data=data)
        return AcmeCertificateStatus.model_validate(response.get("data", response))

    def create_acme_simple(self, domain: str) -> AcmeCertificateStatus:
        """Request a simple single-domain ACME certificate.

        Creates an ACME certificate with default settings:
        - Provider: Let's Encrypt
        - Auto-renew: Enabled

        Args:
            domain: Domain name for the certificate.

        Returns:
            ACME certificate status.
        """
        response = self._post("/certificates", data={"domain": domain})
        data = response.get("data", {})
        # Handle the nested certificate response
        if "certificate" in data:
            return AcmeCertificateStatus.model_validate(
                {
                    "certificateId": data["certificate"]["id"],
                    "name": data["certificate"]["name"],
                    "status": data["certificate"]["status"],
                    "progress": 0,
                    "message": data.get("message", "Certificate pending"),
                    "domains": [
                        d["domain"] for d in data["certificate"].get("domains", [])
                    ],
                }
            )
        return AcmeCertificateStatus.model_validate(data)

    async def create_acme_simple_async(self, domain: str) -> AcmeCertificateStatus:
        """Request a simple single-domain ACME certificate asynchronously.

        Args:
            domain: Domain name for the certificate.

        Returns:
            ACME certificate status.
        """
        response = await self._post_async("/certificates", data={"domain": domain})
        data = response.get("data", {})
        if "certificate" in data:
            return AcmeCertificateStatus.model_validate(
                {
                    "certificateId": data["certificate"]["id"],
                    "name": data["certificate"]["name"],
                    "status": data["certificate"]["status"],
                    "progress": 0,
                    "message": data.get("message", "Certificate pending"),
                    "domains": [
                        d["domain"] for d in data["certificate"].get("domains", [])
                    ],
                }
            )
        return AcmeCertificateStatus.model_validate(data)

    def get_acme_status(self, certificate_id: str) -> AcmeCertificateStatus:
        """Check the status of an ACME certificate.

        Args:
            certificate_id: Certificate ID to check.

        Returns:
            Current status of the ACME certificate.
        """
        response = self._get(
            "/certificates/acme",
            params={"certificateId": certificate_id},
        )
        return AcmeCertificateStatus.model_validate(response.get("data", response))

    async def get_acme_status_async(
        self,
        certificate_id: str,
    ) -> AcmeCertificateStatus:
        """Check the status of an ACME certificate asynchronously.

        Args:
            certificate_id: Certificate ID to check.

        Returns:
            Current status of the ACME certificate.
        """
        response = await self._get_async(
            "/certificates/acme",
            params={"certificateId": certificate_id},
        )
        return AcmeCertificateStatus.model_validate(response.get("data", response))

    def list_acme(self) -> _list[AcmeCertificateStatus]:
        """List all ACME certificates.

        Returns:
            List of ACME certificate statuses.
        """
        response = self._get("/certificates/acme")
        return [
            AcmeCertificateStatus.model_validate(c) for c in response.get("data", [])
        ]

    async def list_acme_async(self) -> _list[AcmeCertificateStatus]:
        """List all ACME certificates asynchronously.

        Returns:
            List of ACME certificate statuses.
        """
        response = await self._get_async("/certificates/acme")
        return [
            AcmeCertificateStatus.model_validate(c) for c in response.get("data", [])
        ]

    def update(
        self,
        domain: str,
        name: str | None = None,
        auto_renew: bool | None = None,
        cert_content: str | None = None,
        key_content: str | None = None,
    ) -> Certificate:
        """Update a certificate.

        Args:
            domain: Domain covered by the certificate.
            name: New display name.
            auto_renew: Enable/disable auto-renewal.
            cert_content: New certificate content (manual only).
            key_content: New private key (required with cert_content).

        Returns:
            The updated certificate.
        """
        data: dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if auto_renew is not None:
            data["autoRenew"] = auto_renew
        if cert_content is not None:
            data["certContent"] = cert_content
        if key_content is not None:
            data["keyContent"] = key_content

        response = self._put("/certificates", data=data, params={"domain": domain})
        return Certificate.model_validate(response.get("data", response))

    async def update_async(
        self,
        domain: str,
        name: str | None = None,
        auto_renew: bool | None = None,
        cert_content: str | None = None,
        key_content: str | None = None,
    ) -> Certificate:
        """Update a certificate asynchronously.

        Args:
            domain: Domain covered by the certificate.
            name: New display name.
            auto_renew: Enable/disable auto-renewal.
            cert_content: New certificate content (manual only).
            key_content: New private key (required with cert_content).

        Returns:
            The updated certificate.
        """
        data: dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if auto_renew is not None:
            data["autoRenew"] = auto_renew
        if cert_content is not None:
            data["certContent"] = cert_content
        if key_content is not None:
            data["keyContent"] = key_content

        response = await self._put_async(
            "/certificates",
            data=data,
            params={"domain": domain},
        )
        return Certificate.model_validate(response.get("data", response))

    def delete(self, domain: str) -> CertificateDeleteResponse:
        """Delete a certificate.

        The certificate cannot be deleted if it is assigned to any zones.

        Args:
            domain: Domain covered by the certificate.

        Returns:
            Deletion confirmation.
        """
        response = self._delete("/certificates", params={"domain": domain})
        return CertificateDeleteResponse.model_validate(response.get("data", response))

    async def delete_async(self, domain: str) -> CertificateDeleteResponse:
        """Delete a certificate asynchronously.

        Args:
            domain: Domain covered by the certificate.

        Returns:
            Deletion confirmation.
        """
        response = await self._delete_async("/certificates", params={"domain": domain})
        return CertificateDeleteResponse.model_validate(response.get("data", response))

    def download(self, certificate_id: str) -> bytes:
        """Download a certificate as a ZIP file.

        The ZIP contains:
        - certificate.pem: The certificate and chain
        - private-key.pem: The private key

        Args:
            certificate_id: Certificate ID to download.

        Returns:
            ZIP file contents as bytes.
        """
        return self._get_raw(f"/certificates/{certificate_id}/download")

    async def download_async(self, certificate_id: str) -> bytes:
        """Download a certificate as a ZIP file asynchronously.

        Args:
            certificate_id: Certificate ID to download.

        Returns:
            ZIP file contents as bytes.
        """
        return await self._get_raw_async(f"/certificates/{certificate_id}/download")
