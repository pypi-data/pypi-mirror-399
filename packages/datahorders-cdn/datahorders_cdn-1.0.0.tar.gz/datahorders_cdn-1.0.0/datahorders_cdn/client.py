"""Main client for the DataHorders CDN SDK."""

from __future__ import annotations

from typing import Any, cast

import httpx

from datahorders_cdn.exceptions import (
    AuthenticationError,
    AuthorizationError,
    CertificateInUseError,
    CircularUpstreamError,
    ConflictError,
    DataHordersError,
    DomainExistsError,
    DomainInUseError,
    DuplicateCertificateError,
    InvalidCertificateError,
    InvalidDomainsError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from datahorders_cdn.resources.analytics import AnalyticsResource
from datahorders_cdn.resources.certificates import CertificatesResource
from datahorders_cdn.resources.domains import DomainsResource
from datahorders_cdn.resources.health_checks import HealthChecksResource
from datahorders_cdn.resources.upstream_servers import UpstreamServersResource
from datahorders_cdn.resources.waf import WafResource
from datahorders_cdn.resources.zones import ZonesResource


class DataHordersCDN:
    """DataHorders CDN API client.

    Provides access to all CDN management APIs including domains, zones,
    certificates, WAF, health checks, and analytics.

    Args:
        api_key: API key for authentication.
        base_url: Base URL for the API (default: https://dashboard.datahorders.org/api/user/v1).
        timeout: Request timeout in seconds (default: 30).
        verify_ssl: Verify SSL certificates (default: True).

    Example:
        >>> from datahorders_cdn import DataHordersCDN
        >>>
        >>> client = DataHordersCDN(api_key="your-api-key")
        >>>
        >>> # List domains
        >>> domains, meta = client.domains.list()
        >>> for domain in domains:
        ...     print(f"{domain.domain} - verified: {domain.verified}")
        >>>
        >>> # Create a zone
        >>> zone = client.zones.create(
        ...     name="app",
        ...     domains=["dom_abc123"],
        ...     servers=[{"address": "10.0.1.100", "port": 8080}],
        ... )

    Async Example:
        >>> import asyncio
        >>> from datahorders_cdn import DataHordersCDN
        >>>
        >>> async def main():
        ...     client = DataHordersCDN(api_key="your-api-key")
        ...     domains, meta = await client.domains.list_async()
        ...     for domain in domains:
        ...         print(f"{domain.domain}")
        ...     client.close()
        >>>
        >>> asyncio.run(main())
    """

    DEFAULT_BASE_URL = "https://dashboard.datahorders.org/api/user/v1"
    DEFAULT_TIMEOUT = 30

    def __init__(
        self,
        api_key: str,
        base_url: str | None = None,
        timeout: int = DEFAULT_TIMEOUT,
        verify_ssl: bool = True,
    ) -> None:
        """Initialize the DataHorders CDN client.

        Args:
            api_key: API key for authentication.
            base_url: Base URL for the API.
            timeout: Request timeout in seconds.
            verify_ssl: Verify SSL certificates.
        """
        self._api_key = api_key
        self._base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self._timeout = timeout
        self._verify_ssl = verify_ssl

        # Create HTTP clients
        self._sync_client: httpx.Client | None = None
        self._async_client: httpx.AsyncClient | None = None

        # Initialize resources
        self.domains = DomainsResource(self)
        self.zones = ZonesResource(self)
        self.certificates = CertificatesResource(self)
        self.health_checks = HealthChecksResource(self)
        self.waf = WafResource(self)
        self.analytics = AnalyticsResource(self)
        self.upstream_servers = UpstreamServersResource(self)

    @property
    def _headers(self) -> dict[str, str]:
        """Get default request headers."""
        return {
            "X-API-Key": self._api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _get_sync_client(self) -> httpx.Client:
        """Get or create synchronous HTTP client."""
        if self._sync_client is None:
            self._sync_client = httpx.Client(
                base_url=self._base_url,
                headers=self._headers,
                timeout=self._timeout,
                verify=self._verify_ssl,
            )
        return self._sync_client

    def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create asynchronous HTTP client."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                base_url=self._base_url,
                headers=self._headers,
                timeout=self._timeout,
                verify=self._verify_ssl,
            )
        return self._async_client

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses from the API.

        Args:
            response: HTTP response object.

        Raises:
            Various DataHordersError subclasses based on response.
        """
        status = response.status_code

        try:
            data = response.json()
        except Exception:
            data = {"error": response.text}

        # Extract error information
        error_data = data.get("error", {})
        if isinstance(error_data, str):
            message = error_data
            code = None
            details = None
        else:
            message = error_data.get("message", str(data))
            code = error_data.get("code")
            details = error_data.get("details")

        # Map status codes to exceptions
        if status == 401:
            raise AuthenticationError(message, code, details)
        elif status == 403:
            raise AuthorizationError(message, code, details)
        elif status == 404:
            raise NotFoundError(message, code, details)
        elif status == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                message,
                code,
                details,
                int(retry_after) if retry_after else None,
            )
        elif status == 409:
            # Handle specific conflict errors
            if code == "DOMAIN_EXISTS":
                raise DomainExistsError(message, code, details)
            elif code == "DOMAIN_IN_USE":
                raise DomainInUseError(message, code, details)
            elif code == "CERTIFICATE_IN_USE":
                raise CertificateInUseError(message, code, details)
            else:
                raise ConflictError(message, code, details)
        elif status == 400:
            # Handle specific validation errors
            if code == "DUPLICATE_DOMAIN_CERTIFICATE":
                existing_id = None
                if isinstance(details, dict):
                    existing_id = details.get("existingCertificateId")
                elif isinstance(error_data, dict) and "data" in error_data:
                    existing_id = error_data["data"].get("existingCertificateId")
                raise DuplicateCertificateError(message, code, details, existing_id)
            elif code == "INVALID_CERTIFICATE":
                raise InvalidCertificateError(message, code, details)
            elif code == "INVALID_DOMAINS":
                missing = []
                if isinstance(details, dict):
                    missing = details.get("missingDomains", [])
                raise InvalidDomainsError(message, code, details, missing)
            elif "Circular upstream" in message or "circular" in message.lower():
                raise CircularUpstreamError(message, code, details)
            else:
                raise ValidationError(message, code, details)
        elif status >= 500:
            raise ServerError(message, code, details)
        else:
            raise DataHordersError(message, code, details)

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a synchronous HTTP request.

        Args:
            method: HTTP method.
            path: API endpoint path.
            params: Query parameters.
            json: JSON request body.

        Returns:
            Response data as dictionary.

        Raises:
            DataHordersError: On API errors.
        """
        client = self._get_sync_client()
        response = client.request(method, path, params=params, json=json)

        if not response.is_success:
            self._handle_error_response(response)

        try:
            return cast(dict[str, Any], response.json())
        except Exception:
            return {"success": True}

    async def _request_async(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an asynchronous HTTP request.

        Args:
            method: HTTP method.
            path: API endpoint path.
            params: Query parameters.
            json: JSON request body.

        Returns:
            Response data as dictionary.

        Raises:
            DataHordersError: On API errors.
        """
        client = self._get_async_client()
        response = await client.request(method, path, params=params, json=json)

        if not response.is_success:
            self._handle_error_response(response)

        try:
            return cast(dict[str, Any], response.json())
        except Exception:
            return {"success": True}

    def _request_raw(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> bytes:
        """Make a synchronous HTTP request and return raw bytes.

        Args:
            method: HTTP method.
            path: API endpoint path.
            params: Query parameters.

        Returns:
            Response content as bytes.

        Raises:
            DataHordersError: On API errors.
        """
        client = self._get_sync_client()
        response = client.request(method, path, params=params)

        if not response.is_success:
            self._handle_error_response(response)

        return response.content

    async def _request_raw_async(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> bytes:
        """Make an asynchronous HTTP request and return raw bytes.

        Args:
            method: HTTP method.
            path: API endpoint path.
            params: Query parameters.

        Returns:
            Response content as bytes.

        Raises:
            DataHordersError: On API errors.
        """
        client = self._get_async_client()
        response = await client.request(method, path, params=params)

        if not response.is_success:
            self._handle_error_response(response)

        return response.content

    def close(self) -> None:
        """Close HTTP clients and release resources."""
        if self._sync_client is not None:
            self._sync_client.close()
            self._sync_client = None
        if self._async_client is not None:
            # Note: For async client, you should use aclose() in async context
            # This is a fallback for sync cleanup
            import asyncio

            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                loop.create_task(self._async_client.aclose())
            else:
                asyncio.run(self._async_client.aclose())
            self._async_client = None

    async def aclose(self) -> None:
        """Asynchronously close HTTP clients and release resources."""
        if self._sync_client is not None:
            self._sync_client.close()
            self._sync_client = None
        if self._async_client is not None:
            await self._async_client.aclose()
            self._async_client = None

    def __enter__(self) -> DataHordersCDN:
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()

    async def __aenter__(self) -> DataHordersCDN:
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.aclose()
