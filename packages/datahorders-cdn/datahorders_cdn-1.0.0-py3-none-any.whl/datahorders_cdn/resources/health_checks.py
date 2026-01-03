"""Health checks resource for the DataHorders CDN SDK."""

from __future__ import annotations

from typing import Any, cast

from datahorders_cdn.models import (
    CdnNode,
    HealthCheckMethod,
    HealthCheckProfile,
    HealthCheckProtocol,
    HealthCheckToggleResponse,
)
from datahorders_cdn.resources.base import BaseResource


class HealthChecksResource(BaseResource):
    """Resource for managing health checks.

    Health checks automatically detect failed backends and remove them
    from the load balancer rotation.
    """

    def list_profiles(
        self,
        page: int = 1,
        limit: int = 10,
        search: str | None = None,
    ) -> tuple[list[HealthCheckProfile], dict[str, Any]]:
        """List health check profiles.

        Args:
            page: Page number.
            limit: Items per page.
            search: Search by name or description.

        Returns:
            Tuple of (list of profiles, pagination dict).
        """
        params: dict[str, Any] = {"page": page, "limit": limit}
        if search:
            params["search"] = search

        response = self._get("/healthcheck-profiles", params=params)
        profiles = [
            HealthCheckProfile.model_validate(p) for p in response.get("profiles", [])
        ]
        pagination = response.get("pagination", {})
        return profiles, pagination

    async def list_profiles_async(
        self,
        page: int = 1,
        limit: int = 10,
        search: str | None = None,
    ) -> tuple[list[HealthCheckProfile], dict[str, Any]]:
        """List health check profiles asynchronously.

        Args:
            page: Page number.
            limit: Items per page.
            search: Search by name or description.

        Returns:
            Tuple of (list of profiles, pagination dict).
        """
        params: dict[str, Any] = {"page": page, "limit": limit}
        if search:
            params["search"] = search

        response = await self._get_async("/healthcheck-profiles", params=params)
        profiles = [
            HealthCheckProfile.model_validate(p) for p in response.get("profiles", [])
        ]
        pagination = response.get("pagination", {})
        return profiles, pagination

    def get_profile(self, profile_id: str) -> HealthCheckProfile:
        """Get a specific health check profile.

        Args:
            profile_id: Profile ID.

        Returns:
            The health check profile.
        """
        response = self._get(f"/healthcheck-profiles/{profile_id}")
        return HealthCheckProfile.model_validate(response.get("profile", response))

    async def get_profile_async(self, profile_id: str) -> HealthCheckProfile:
        """Get a specific health check profile asynchronously.

        Args:
            profile_id: Profile ID.

        Returns:
            The health check profile.
        """
        response = await self._get_async(f"/healthcheck-profiles/{profile_id}")
        return HealthCheckProfile.model_validate(response.get("profile", response))

    def create_profile(
        self,
        name: str,
        description: str | None = None,
        protocol: HealthCheckProtocol = HealthCheckProtocol.HTTP,
        port: int = 80,
        path: str = "/",
        method: HealthCheckMethod = HealthCheckMethod.HEAD,
        expected_status_codes: str = "200-399",
        expected_response_text: str | None = None,
        check_interval: int = 30,
        timeout: int = 10,
        retries: int = 2,
        follow_redirects: bool = False,
        verify_ssl: bool = False,
        custom_headers: dict[str, str] | None = None,
    ) -> HealthCheckProfile:
        """Create a health check profile.

        Args:
            name: Profile name (unique per user).
            description: Profile description.
            protocol: 'http', 'https', or 'tcp'.
            port: Port to check (0-65535).
            path: URL path for HTTP/HTTPS checks.
            method: HTTP method: 'HEAD', 'GET', 'POST'.
            expected_status_codes: Expected codes (e.g., '200', '200-299').
            expected_response_text: Text to find in response body.
            check_interval: Seconds between checks (5-3600).
            timeout: Request timeout in seconds (1-300).
            retries: Retries before marking unhealthy (0-10).
            follow_redirects: Follow HTTP redirects.
            verify_ssl: Verify SSL certificates (HTTPS).
            custom_headers: Custom HTTP headers to send.

        Returns:
            The created profile.
        """
        data: dict[str, Any] = {
            "name": name,
            "protocol": protocol.value,
            "port": port,
            "path": path,
            "method": method.value,
            "expectedStatusCodes": expected_status_codes,
            "checkInterval": check_interval,
            "timeout": timeout,
            "retries": retries,
            "followRedirects": follow_redirects,
            "verifySSL": verify_ssl,
        }
        if description:
            data["description"] = description
        if expected_response_text:
            data["expectedResponseText"] = expected_response_text
        if custom_headers:
            data["customHeaders"] = custom_headers

        response = self._post("/healthcheck-profiles", data=data)
        return HealthCheckProfile.model_validate(response.get("profile", response))

    async def create_profile_async(
        self,
        name: str,
        description: str | None = None,
        protocol: HealthCheckProtocol = HealthCheckProtocol.HTTP,
        port: int = 80,
        path: str = "/",
        method: HealthCheckMethod = HealthCheckMethod.HEAD,
        expected_status_codes: str = "200-399",
        expected_response_text: str | None = None,
        check_interval: int = 30,
        timeout: int = 10,
        retries: int = 2,
        follow_redirects: bool = False,
        verify_ssl: bool = False,
        custom_headers: dict[str, str] | None = None,
    ) -> HealthCheckProfile:
        """Create a health check profile asynchronously.

        Args:
            name: Profile name.
            description: Profile description.
            protocol: Check protocol.
            port: Port to check.
            path: URL path.
            method: HTTP method.
            expected_status_codes: Expected codes.
            expected_response_text: Expected response text.
            check_interval: Seconds between checks.
            timeout: Request timeout.
            retries: Retries before unhealthy.
            follow_redirects: Follow redirects.
            verify_ssl: Verify SSL.
            custom_headers: Custom headers.

        Returns:
            The created profile.
        """
        data: dict[str, Any] = {
            "name": name,
            "protocol": protocol.value,
            "port": port,
            "path": path,
            "method": method.value,
            "expectedStatusCodes": expected_status_codes,
            "checkInterval": check_interval,
            "timeout": timeout,
            "retries": retries,
            "followRedirects": follow_redirects,
            "verifySSL": verify_ssl,
        }
        if description:
            data["description"] = description
        if expected_response_text:
            data["expectedResponseText"] = expected_response_text
        if custom_headers:
            data["customHeaders"] = custom_headers

        response = await self._post_async("/healthcheck-profiles", data=data)
        return HealthCheckProfile.model_validate(response.get("profile", response))

    def update_profile(
        self,
        profile_id: str,
        name: str | None = None,
        description: str | None = None,
        protocol: HealthCheckProtocol | None = None,
        port: int | None = None,
        path: str | None = None,
        method: HealthCheckMethod | None = None,
        expected_status_codes: str | None = None,
        expected_response_text: str | None = None,
        check_interval: int | None = None,
        timeout: int | None = None,
        retries: int | None = None,
        follow_redirects: bool | None = None,
        verify_ssl: bool | None = None,
        custom_headers: dict[str, str] | None = None,
    ) -> HealthCheckProfile:
        """Update a health check profile.

        Args:
            profile_id: Profile ID to update.
            name: Profile name.
            description: Profile description.
            protocol: Check protocol.
            port: Port to check.
            path: URL path.
            method: HTTP method.
            expected_status_codes: Expected codes.
            expected_response_text: Expected response text.
            check_interval: Seconds between checks.
            timeout: Request timeout.
            retries: Retries before unhealthy.
            follow_redirects: Follow redirects.
            verify_ssl: Verify SSL.
            custom_headers: Custom headers.

        Returns:
            The updated profile.
        """
        data: dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if protocol is not None:
            data["protocol"] = protocol.value
        if port is not None:
            data["port"] = port
        if path is not None:
            data["path"] = path
        if method is not None:
            data["method"] = method.value
        if expected_status_codes is not None:
            data["expectedStatusCodes"] = expected_status_codes
        if expected_response_text is not None:
            data["expectedResponseText"] = expected_response_text
        if check_interval is not None:
            data["checkInterval"] = check_interval
        if timeout is not None:
            data["timeout"] = timeout
        if retries is not None:
            data["retries"] = retries
        if follow_redirects is not None:
            data["followRedirects"] = follow_redirects
        if verify_ssl is not None:
            data["verifySSL"] = verify_ssl
        if custom_headers is not None:
            data["customHeaders"] = custom_headers

        response = self._put(f"/healthcheck-profiles/{profile_id}", data=data)
        return HealthCheckProfile.model_validate(response.get("profile", response))

    async def update_profile_async(
        self,
        profile_id: str,
        **kwargs: Any,
    ) -> HealthCheckProfile:
        """Update a health check profile asynchronously.

        Args:
            profile_id: Profile ID to update.
            **kwargs: Profile fields to update.

        Returns:
            The updated profile.
        """
        data: dict[str, Any] = {}
        field_mapping = {
            "name": "name",
            "description": "description",
            "port": "port",
            "path": "path",
            "expected_status_codes": "expectedStatusCodes",
            "expected_response_text": "expectedResponseText",
            "check_interval": "checkInterval",
            "timeout": "timeout",
            "retries": "retries",
            "follow_redirects": "followRedirects",
            "verify_ssl": "verifySSL",
            "custom_headers": "customHeaders",
        }
        for py_key, api_key in field_mapping.items():
            if py_key in kwargs and kwargs[py_key] is not None:
                data[api_key] = kwargs[py_key]

        if "protocol" in kwargs and kwargs["protocol"] is not None:
            data["protocol"] = kwargs["protocol"].value
        if "method" in kwargs and kwargs["method"] is not None:
            data["method"] = kwargs["method"].value

        response = await self._put_async(
            f"/healthcheck-profiles/{profile_id}",
            data=data,
        )
        return HealthCheckProfile.model_validate(response.get("profile", response))

    def delete_profile(self, profile_id: str) -> bool:
        """Delete a health check profile.

        Cannot delete profiles in use by servers.

        Args:
            profile_id: Profile ID to delete.

        Returns:
            True if successful.
        """
        response = self._delete(f"/healthcheck-profiles/{profile_id}")
        return cast(bool, response.get("success", True))

    async def delete_profile_async(self, profile_id: str) -> bool:
        """Delete a health check profile asynchronously.

        Args:
            profile_id: Profile ID to delete.

        Returns:
            True if successful.
        """
        response = await self._delete_async(f"/healthcheck-profiles/{profile_id}")
        return cast(bool, response.get("success", True))

    def toggle_server_health_check(
        self,
        server_id: str,
        action: str,
        reason: str | None = None,
    ) -> HealthCheckToggleResponse:
        """Enable or disable health checks for a server.

        Args:
            server_id: Server ID.
            action: 'enable' or 'disable'.
            reason: Reason for disabling (used with 'disable').

        Returns:
            Toggle response.
        """
        data: dict[str, Any] = {
            "serverId": server_id,
            "action": action,
        }
        if reason and action == "disable":
            data["reason"] = reason

        response = self._post("/monitoring/health-checks", data=data)
        return HealthCheckToggleResponse.model_validate(response)

    async def toggle_server_health_check_async(
        self,
        server_id: str,
        action: str,
        reason: str | None = None,
    ) -> HealthCheckToggleResponse:
        """Enable or disable health checks for a server asynchronously.

        Args:
            server_id: Server ID.
            action: 'enable' or 'disable'.
            reason: Reason for disabling.

        Returns:
            Toggle response.
        """
        data: dict[str, Any] = {
            "serverId": server_id,
            "action": action,
        }
        if reason and action == "disable":
            data["reason"] = reason

        response = await self._post_async("/monitoring/health-checks", data=data)
        return HealthCheckToggleResponse.model_validate(response)

    def enable_server(self, server_id: str) -> HealthCheckToggleResponse:
        """Enable health checks for a server.

        Args:
            server_id: Server ID.

        Returns:
            Toggle response.
        """
        return self.toggle_server_health_check(server_id, "enable")

    async def enable_server_async(
        self,
        server_id: str,
    ) -> HealthCheckToggleResponse:
        """Enable health checks for a server asynchronously.

        Args:
            server_id: Server ID.

        Returns:
            Toggle response.
        """
        return await self.toggle_server_health_check_async(server_id, "enable")

    def disable_server(
        self,
        server_id: str,
        reason: str | None = None,
    ) -> HealthCheckToggleResponse:
        """Disable health checks for a server.

        Args:
            server_id: Server ID.
            reason: Reason for disabling.

        Returns:
            Toggle response.
        """
        return self.toggle_server_health_check(server_id, "disable", reason)

    async def disable_server_async(
        self,
        server_id: str,
        reason: str | None = None,
    ) -> HealthCheckToggleResponse:
        """Disable health checks for a server asynchronously.

        Args:
            server_id: Server ID.
            reason: Reason for disabling.

        Returns:
            Toggle response.
        """
        return await self.toggle_server_health_check_async(
            server_id,
            "disable",
            reason,
        )

    def list_cdn_nodes(self) -> list[CdnNode]:
        """List CDN edge node status.

        Returns:
            List of CDN nodes.
        """
        response = self._get("/cdn-nodes")
        # Response is a list, not wrapped in data
        if isinstance(response, list):
            return [CdnNode.model_validate(n) for n in response]
        return [CdnNode.model_validate(n) for n in response.get("data", response)]

    async def list_cdn_nodes_async(self) -> list[CdnNode]:
        """List CDN edge node status asynchronously.

        Returns:
            List of CDN nodes.
        """
        response = await self._get_async("/cdn-nodes")
        if isinstance(response, list):
            return [CdnNode.model_validate(n) for n in response]
        return [CdnNode.model_validate(n) for n in response.get("data", response)]
