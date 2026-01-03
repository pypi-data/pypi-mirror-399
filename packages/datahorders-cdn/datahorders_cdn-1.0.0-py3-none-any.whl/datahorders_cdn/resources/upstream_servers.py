"""Upstream servers resource for the DataHorders CDN SDK."""

from __future__ import annotations

import builtins
from typing import Any, cast

from datahorders_cdn.models import ServerProtocol, UpstreamServer
from datahorders_cdn.resources.base import BaseResource

# Alias to avoid shadowing by the `list` method in classes
_list = builtins.list


class UpstreamServersResource(BaseResource):
    """Resource for managing upstream backend servers.

    Upstream servers form a pool that receives traffic from zones
    with configurable load balancing.
    """

    def list(self, zone_id: str) -> _list[UpstreamServer]:
        """List servers in a zone's upstream pool.

        Args:
            zone_id: The zone ID.

        Returns:
            List of upstream servers.
        """
        response = self._get(f"/zones/{zone_id}/upstream/servers")
        # Response is a list, not wrapped in data
        if isinstance(response, list):
            return [UpstreamServer.model_validate(s) for s in response]
        return [
            UpstreamServer.model_validate(s) for s in response.get("data", response)
        ]

    async def list_async(self, zone_id: str) -> _list[UpstreamServer]:
        """List servers in a zone's upstream pool asynchronously.

        Args:
            zone_id: The zone ID.

        Returns:
            List of upstream servers.
        """
        response = await self._get_async(f"/zones/{zone_id}/upstream/servers")
        if isinstance(response, list):
            return [UpstreamServer.model_validate(s) for s in response]
        return [
            UpstreamServer.model_validate(s) for s in response.get("data", response)
        ]

    def create(
        self,
        zone_id: str,
        name: str,
        address: str,
        port: int,
        health_check_path: str,
        protocol: ServerProtocol = ServerProtocol.HTTP,
        weight: int = 1,
        backup: bool = False,
        region: str | None = None,
        country: str | None = None,
    ) -> UpstreamServer:
        """Add a server to the zone's upstream pool.

        Args:
            zone_id: The zone ID.
            name: Server display name.
            address: IP address or hostname of the backend.
            port: Port number (1-65535).
            health_check_path: Path for health checks (e.g., '/health').
            protocol: 'http' or 'https'.
            weight: Load balancing weight 1-100.
            backup: Use as backup server.
            region: Geographic region code.
            country: ISO country code.

        Returns:
            The created server.
        """
        data: dict[str, Any] = {
            "name": name,
            "address": address,
            "port": port,
            "protocol": protocol.value,
            "weight": weight,
            "backup": backup,
            "healthCheckPath": health_check_path,
        }
        if region:
            data["region"] = region
        if country:
            data["country"] = country

        response = self._post(f"/zones/{zone_id}/upstream/servers", data=data)
        return UpstreamServer.model_validate(response.get("data", response))

    async def create_async(
        self,
        zone_id: str,
        name: str,
        address: str,
        port: int,
        health_check_path: str,
        protocol: ServerProtocol = ServerProtocol.HTTP,
        weight: int = 1,
        backup: bool = False,
        region: str | None = None,
        country: str | None = None,
    ) -> UpstreamServer:
        """Add a server to the zone's upstream pool asynchronously.

        Args:
            zone_id: The zone ID.
            name: Server display name.
            address: IP address or hostname.
            port: Port number.
            health_check_path: Health check path.
            protocol: Protocol.
            weight: Load balancing weight.
            backup: Use as backup.
            region: Region code.
            country: Country code.

        Returns:
            The created server.
        """
        data: dict[str, Any] = {
            "name": name,
            "address": address,
            "port": port,
            "protocol": protocol.value,
            "weight": weight,
            "backup": backup,
            "healthCheckPath": health_check_path,
        }
        if region:
            data["region"] = region
        if country:
            data["country"] = country

        response = await self._post_async(
            f"/zones/{zone_id}/upstream/servers",
            data=data,
        )
        return UpstreamServer.model_validate(response.get("data", response))

    def update(
        self,
        zone_id: str,
        server_id: str,
        name: str | None = None,
        address: str | None = None,
        port: int | None = None,
        protocol: ServerProtocol | None = None,
        weight: int | None = None,
        backup: bool | None = None,
        health_check_path: str | None = None,
        region: str | None = None,
        country: str | None = None,
    ) -> UpstreamServer:
        """Update an upstream server.

        Args:
            zone_id: The zone ID.
            server_id: The server ID.
            name: Server display name.
            address: IP address or hostname.
            port: Port number.
            protocol: Protocol.
            weight: Load balancing weight.
            backup: Use as backup.
            health_check_path: Health check path.
            region: Region code.
            country: Country code.

        Returns:
            The updated server.
        """
        data: dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if address is not None:
            data["address"] = address
        if port is not None:
            data["port"] = port
        if protocol is not None:
            data["protocol"] = protocol.value
        if weight is not None:
            data["weight"] = weight
        if backup is not None:
            data["backup"] = backup
        if health_check_path is not None:
            data["healthCheckPath"] = health_check_path
        if region is not None:
            data["region"] = region
        if country is not None:
            data["country"] = country

        response = self._put(
            f"/zones/{zone_id}/upstream/servers/{server_id}",
            data=data,
        )
        return UpstreamServer.model_validate(response.get("data", response))

    async def update_async(
        self,
        zone_id: str,
        server_id: str,
        name: str | None = None,
        address: str | None = None,
        port: int | None = None,
        protocol: ServerProtocol | None = None,
        weight: int | None = None,
        backup: bool | None = None,
        health_check_path: str | None = None,
        region: str | None = None,
        country: str | None = None,
    ) -> UpstreamServer:
        """Update an upstream server asynchronously.

        Args:
            zone_id: The zone ID.
            server_id: The server ID.
            name: Server display name.
            address: IP address or hostname.
            port: Port number.
            protocol: Protocol.
            weight: Load balancing weight.
            backup: Use as backup.
            health_check_path: Health check path.
            region: Region code.
            country: Country code.

        Returns:
            The updated server.
        """
        data: dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if address is not None:
            data["address"] = address
        if port is not None:
            data["port"] = port
        if protocol is not None:
            data["protocol"] = protocol.value
        if weight is not None:
            data["weight"] = weight
        if backup is not None:
            data["backup"] = backup
        if health_check_path is not None:
            data["healthCheckPath"] = health_check_path
        if region is not None:
            data["region"] = region
        if country is not None:
            data["country"] = country

        response = await self._put_async(
            f"/zones/{zone_id}/upstream/servers/{server_id}",
            data=data,
        )
        return UpstreamServer.model_validate(response.get("data", response))

    def delete(self, zone_id: str, server_id: str) -> bool:
        """Remove a server from the upstream pool.

        Args:
            zone_id: The zone ID.
            server_id: The server ID.

        Returns:
            True if successful.
        """
        response = self._delete(f"/zones/{zone_id}/upstream/servers/{server_id}")
        return cast(bool, response.get("success", True))

    async def delete_async(self, zone_id: str, server_id: str) -> bool:
        """Remove a server from the upstream pool asynchronously.

        Args:
            zone_id: The zone ID.
            server_id: The server ID.

        Returns:
            True if successful.
        """
        response = await self._delete_async(
            f"/zones/{zone_id}/upstream/servers/{server_id}"
        )
        return cast(bool, response.get("success", True))
