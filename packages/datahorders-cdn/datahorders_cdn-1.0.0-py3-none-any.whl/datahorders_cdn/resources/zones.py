"""Zones resource for the DataHorders CDN SDK."""

from __future__ import annotations

import builtins
from typing import Any

from datahorders_cdn.models import (
    LoadBalanceMethod,
    PaginationMeta,
    Zone,
    ZoneDeleteResponse,
)
from datahorders_cdn.resources.base import BaseResource

# Alias to avoid shadowing by the `list` method in classes
_list = builtins.list


class ZonesResource(BaseResource):
    """Resource for managing zones.

    Zones define how traffic is routed from domains to upstream backend servers.
    """

    def list(
        self,
        page: int = 1,
        per_page: int = 10,
        domain: str | None = None,
    ) -> tuple[_list[Zone], PaginationMeta]:
        """List all zones.

        Args:
            page: Page number (1-indexed).
            per_page: Items per page.
            domain: Filter by domain name (partial match).

        Returns:
            Tuple of (list of zones, pagination metadata).
        """
        params: dict[str, Any] = {"page": page, "perPage": per_page}
        if domain:
            params["domain"] = domain

        response = self._get("/zones", params=params)
        zones = [Zone.model_validate(z) for z in response.get("data", [])]
        meta = PaginationMeta.model_validate(response.get("meta", {}))
        return zones, meta

    async def list_async(
        self,
        page: int = 1,
        per_page: int = 10,
        domain: str | None = None,
    ) -> tuple[_list[Zone], PaginationMeta]:
        """List all zones asynchronously.

        Args:
            page: Page number (1-indexed).
            per_page: Items per page.
            domain: Filter by domain name (partial match).

        Returns:
            Tuple of (list of zones, pagination metadata).
        """
        params: dict[str, Any] = {"page": page, "perPage": per_page}
        if domain:
            params["domain"] = domain

        response = await self._get_async("/zones", params=params)
        zones = [Zone.model_validate(z) for z in response.get("data", [])]
        meta = PaginationMeta.model_validate(response.get("meta", {}))
        return zones, meta

    def get(self, zone_id: str) -> Zone:
        """Get a zone by ID.

        Args:
            zone_id: The zone ID.

        Returns:
            The zone object.
        """
        response = self._get(f"/zones/{zone_id}")
        return Zone.model_validate(response.get("data", response))

    async def get_async(self, zone_id: str) -> Zone:
        """Get a zone by ID asynchronously.

        Args:
            zone_id: The zone ID.

        Returns:
            The zone object.
        """
        response = await self._get_async(f"/zones/{zone_id}")
        return Zone.model_validate(response.get("data", response))

    def get_by_fqdn(self, fqdn: str) -> Zone:
        """Get a zone by fully qualified domain name.

        Args:
            fqdn: Fully qualified domain name (e.g., 'app.example.com').
                  Use '@.example.com' for apex domain.

        Returns:
            The zone object.
        """
        response = self._get("/zones", params={"fqdn": fqdn})
        return Zone.model_validate(response.get("data", response))

    async def get_by_fqdn_async(self, fqdn: str) -> Zone:
        """Get a zone by fully qualified domain name asynchronously.

        Args:
            fqdn: Fully qualified domain name (e.g., 'app.example.com').
                  Use '@.example.com' for apex domain.

        Returns:
            The zone object.
        """
        response = await self._get_async("/zones", params={"fqdn": fqdn})
        return Zone.model_validate(response.get("data", response))

    def create(
        self,
        name: str,
        domains: _list[str],
        servers: _list[dict[str, Any]],
        certificate_id: str | None = None,
        load_balance_method: LoadBalanceMethod = LoadBalanceMethod.ROUND_ROBIN,
        upgrade_insecure: bool = True,
        four_k_fallback: bool = False,
        health_check_enabled: bool = False,
    ) -> Zone:
        """Create a new zone.

        Args:
            name: Zone name (subdomain or '@' for apex).
            domains: List of domain IDs (minimum 1).
            servers: List of upstream server configurations.
                Each server should have: address (required), port, protocol,
                name, weight, backup, healthCheckPath.
            certificate_id: SSL certificate ID (auto-detected if omitted).
            load_balance_method: Load balancing method.
            upgrade_insecure: Upgrade HTTP to HTTPS.
            four_k_fallback: Enable 4K content fallback.
            health_check_enabled: Enable health checks.

        Returns:
            The created zone.

        Example:
            >>> zone = client.zones.create(
            ...     name="app",
            ...     domains=["dom_abc123"],
            ...     servers=[
            ...         {
            ...             "address": "10.0.1.100",
            ...             "port": 8080,
            ...             "protocol": "http",
            ...             "healthCheckPath": "/health",
            ...         }
            ...     ],
            ... )
        """
        # Build upstream configuration
        upstream_servers = []
        for server in servers:
            srv = {
                "address": server["address"],
                "port": server.get("port", 80),
                "protocol": server.get("protocol", "http"),
            }
            if "name" in server:
                srv["name"] = server["name"]
            if "weight" in server:
                srv["weight"] = server["weight"]
            if "backup" in server:
                srv["backup"] = server["backup"]
            if "healthCheckPath" in server:
                srv["healthCheckPath"] = server["healthCheckPath"]
            upstream_servers.append(srv)

        data: dict[str, Any] = {
            "name": name,
            "domains": domains,
            "upgradeInsecure": upgrade_insecure,
            "fourKFallback": four_k_fallback,
            "healthCheckEnabled": health_check_enabled,
            "upstream": {
                "loadBalanceMethod": load_balance_method.value,
                "servers": upstream_servers,
            },
        }
        if certificate_id:
            data["certificateId"] = certificate_id

        response = self._post("/zones", data=data)
        return Zone.model_validate(response.get("data", response))

    async def create_async(
        self,
        name: str,
        domains: _list[str],
        servers: _list[dict[str, Any]],
        certificate_id: str | None = None,
        load_balance_method: LoadBalanceMethod = LoadBalanceMethod.ROUND_ROBIN,
        upgrade_insecure: bool = True,
        four_k_fallback: bool = False,
        health_check_enabled: bool = False,
    ) -> Zone:
        """Create a new zone asynchronously.

        Args:
            name: Zone name (subdomain or '@' for apex).
            domains: List of domain IDs (minimum 1).
            servers: List of upstream server configurations.
            certificate_id: SSL certificate ID (auto-detected if omitted).
            load_balance_method: Load balancing method.
            upgrade_insecure: Upgrade HTTP to HTTPS.
            four_k_fallback: Enable 4K content fallback.
            health_check_enabled: Enable health checks.

        Returns:
            The created zone.
        """
        upstream_servers = []
        for server in servers:
            srv = {
                "address": server["address"],
                "port": server.get("port", 80),
                "protocol": server.get("protocol", "http"),
            }
            if "name" in server:
                srv["name"] = server["name"]
            if "weight" in server:
                srv["weight"] = server["weight"]
            if "backup" in server:
                srv["backup"] = server["backup"]
            if "healthCheckPath" in server:
                srv["healthCheckPath"] = server["healthCheckPath"]
            upstream_servers.append(srv)

        data: dict[str, Any] = {
            "name": name,
            "domains": domains,
            "upgradeInsecure": upgrade_insecure,
            "fourKFallback": four_k_fallback,
            "healthCheckEnabled": health_check_enabled,
            "upstream": {
                "loadBalanceMethod": load_balance_method.value,
                "servers": upstream_servers,
            },
        }
        if certificate_id:
            data["certificateId"] = certificate_id

        response = await self._post_async("/zones", data=data)
        return Zone.model_validate(response.get("data", response))

    def update(
        self,
        zone_id: str | None = None,
        fqdn: str | None = None,
        name: str | None = None,
        domains: _list[str] | None = None,
        certificate_id: str | None = None,
        force_certificate_removal: bool = False,
        upgrade_insecure: bool | None = None,
        four_k_fallback: bool | None = None,
        health_check_enabled: bool | None = None,
        load_balance_method: LoadBalanceMethod | None = None,
        servers: _list[dict[str, Any]] | None = None,
    ) -> Zone:
        """Update a zone.

        Provide either zone_id or fqdn to identify the zone.

        Args:
            zone_id: Zone ID to update.
            fqdn: FQDN of the zone to update.
            name: New zone name.
            domains: Updated list of domain IDs.
            certificate_id: New certificate ID (None to auto-detect).
            force_certificate_removal: Force remove certificate.
            upgrade_insecure: Upgrade HTTP to HTTPS.
            four_k_fallback: Enable 4K fallback.
            health_check_enabled: Enable health checks.
            load_balance_method: Load balancing method.
            servers: Updated upstream server configurations.

        Returns:
            The updated zone.

        Raises:
            ValueError: If neither zone_id nor fqdn is provided.
        """
        if not zone_id and not fqdn:
            raise ValueError("Either zone_id or fqdn must be provided")

        data: dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if domains is not None:
            data["domains"] = domains
        if certificate_id is not None:
            data["certificateId"] = certificate_id
        if force_certificate_removal:
            data["forceCertificateRemoval"] = True
        if upgrade_insecure is not None:
            data["upgradeInsecure"] = upgrade_insecure
        if four_k_fallback is not None:
            data["fourKFallback"] = four_k_fallback
        if health_check_enabled is not None:
            data["healthCheckEnabled"] = health_check_enabled

        if load_balance_method is not None or servers is not None:
            upstream: dict[str, Any] = {}
            if load_balance_method is not None:
                upstream["loadBalanceMethod"] = load_balance_method.value
            if servers is not None:
                upstream_servers = []
                for server in servers:
                    srv = {
                        "address": server["address"],
                        "port": server.get("port", 80),
                        "protocol": server.get("protocol", "http"),
                    }
                    if "id" in server:
                        srv["id"] = server["id"]
                    if "name" in server:
                        srv["name"] = server["name"]
                    if "weight" in server:
                        srv["weight"] = server["weight"]
                    if "backup" in server:
                        srv["backup"] = server["backup"]
                    if "healthCheckPath" in server:
                        srv["healthCheckPath"] = server["healthCheckPath"]
                    upstream_servers.append(srv)
                upstream["servers"] = upstream_servers
            data["upstream"] = upstream

        if zone_id:
            response = self._put(f"/zones/{zone_id}", data=data)
        else:
            response = self._patch("/zones", data=data, params={"fqdn": fqdn})

        return Zone.model_validate(response.get("data", response))

    async def update_async(
        self,
        zone_id: str | None = None,
        fqdn: str | None = None,
        name: str | None = None,
        domains: _list[str] | None = None,
        certificate_id: str | None = None,
        force_certificate_removal: bool = False,
        upgrade_insecure: bool | None = None,
        four_k_fallback: bool | None = None,
        health_check_enabled: bool | None = None,
        load_balance_method: LoadBalanceMethod | None = None,
        servers: _list[dict[str, Any]] | None = None,
    ) -> Zone:
        """Update a zone asynchronously.

        Provide either zone_id or fqdn to identify the zone.

        Args:
            zone_id: Zone ID to update.
            fqdn: FQDN of the zone to update.
            name: New zone name.
            domains: Updated list of domain IDs.
            certificate_id: New certificate ID (None to auto-detect).
            force_certificate_removal: Force remove certificate.
            upgrade_insecure: Upgrade HTTP to HTTPS.
            four_k_fallback: Enable 4K fallback.
            health_check_enabled: Enable health checks.
            load_balance_method: Load balancing method.
            servers: Updated upstream server configurations.

        Returns:
            The updated zone.

        Raises:
            ValueError: If neither zone_id nor fqdn is provided.
        """
        if not zone_id and not fqdn:
            raise ValueError("Either zone_id or fqdn must be provided")

        data: dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if domains is not None:
            data["domains"] = domains
        if certificate_id is not None:
            data["certificateId"] = certificate_id
        if force_certificate_removal:
            data["forceCertificateRemoval"] = True
        if upgrade_insecure is not None:
            data["upgradeInsecure"] = upgrade_insecure
        if four_k_fallback is not None:
            data["fourKFallback"] = four_k_fallback
        if health_check_enabled is not None:
            data["healthCheckEnabled"] = health_check_enabled

        if load_balance_method is not None or servers is not None:
            upstream: dict[str, Any] = {}
            if load_balance_method is not None:
                upstream["loadBalanceMethod"] = load_balance_method.value
            if servers is not None:
                upstream_servers = []
                for server in servers:
                    srv = {
                        "address": server["address"],
                        "port": server.get("port", 80),
                        "protocol": server.get("protocol", "http"),
                    }
                    if "id" in server:
                        srv["id"] = server["id"]
                    if "name" in server:
                        srv["name"] = server["name"]
                    if "weight" in server:
                        srv["weight"] = server["weight"]
                    if "backup" in server:
                        srv["backup"] = server["backup"]
                    if "healthCheckPath" in server:
                        srv["healthCheckPath"] = server["healthCheckPath"]
                    upstream_servers.append(srv)
                upstream["servers"] = upstream_servers
            data["upstream"] = upstream

        if zone_id:
            response = await self._put_async(f"/zones/{zone_id}", data=data)
        else:
            response = await self._patch_async(
                "/zones", data=data, params={"fqdn": fqdn}
            )

        return Zone.model_validate(response.get("data", response))

    def delete(
        self,
        zone_id: str | None = None,
        fqdn: str | None = None,
    ) -> ZoneDeleteResponse:
        """Delete a zone.

        Provide either zone_id or fqdn to identify the zone.
        This performs a soft-delete (data retained for billing).

        Args:
            zone_id: Zone ID to delete.
            fqdn: FQDN of the zone to delete.

        Returns:
            Deletion confirmation.

        Raises:
            ValueError: If neither zone_id nor fqdn is provided.
        """
        if not zone_id and not fqdn:
            raise ValueError("Either zone_id or fqdn must be provided")

        if zone_id:
            response = self._delete(f"/zones/{zone_id}")
        else:
            response = self._delete("/zones", params={"fqdn": fqdn})

        return ZoneDeleteResponse.model_validate(response.get("data", response))

    async def delete_async(
        self,
        zone_id: str | None = None,
        fqdn: str | None = None,
    ) -> ZoneDeleteResponse:
        """Delete a zone asynchronously.

        Provide either zone_id or fqdn to identify the zone.
        This performs a soft-delete (data retained for billing).

        Args:
            zone_id: Zone ID to delete.
            fqdn: FQDN of the zone to delete.

        Returns:
            Deletion confirmation.

        Raises:
            ValueError: If neither zone_id nor fqdn is provided.
        """
        if not zone_id and not fqdn:
            raise ValueError("Either zone_id or fqdn must be provided")

        if zone_id:
            response = await self._delete_async(f"/zones/{zone_id}")
        else:
            response = await self._delete_async("/zones", params={"fqdn": fqdn})

        return ZoneDeleteResponse.model_validate(response.get("data", response))
