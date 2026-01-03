"""WAF resource for the DataHorders CDN SDK."""

from __future__ import annotations

from datetime import datetime
from typing import Any, cast

from datahorders_cdn.models import (
    IpListType,
    PaginationMeta,
    WafAction,
    WafAsnRule,
    WafConfigResponse,
    WafCountryRule,
    WafIpEntry,
    WafMatchTarget,
    WafMode,
    WafRule,
    WafRuleType,
    WafSeverity,
)
from datahorders_cdn.resources.base import BaseResource


class WafResource(BaseResource):
    """Resource for managing Web Application Firewall settings.

    Provides protection against common web attacks including SQL injection,
    XSS, and more.
    """

    # ========================================================================
    # WAF Configuration
    # ========================================================================

    def get_config(self, zone_id: str) -> WafConfigResponse:
        """Get WAF configuration for a zone.

        Args:
            zone_id: The zone ID.

        Returns:
            WAF configuration and statistics.
        """
        response = self._get(f"/zones/{zone_id}/waf")
        return WafConfigResponse.model_validate(response.get("data", response))

    async def get_config_async(self, zone_id: str) -> WafConfigResponse:
        """Get WAF configuration for a zone asynchronously.

        Args:
            zone_id: The zone ID.

        Returns:
            WAF configuration and statistics.
        """
        response = await self._get_async(f"/zones/{zone_id}/waf")
        return WafConfigResponse.model_validate(response.get("data", response))

    def update_config(
        self,
        zone_id: str,
        enabled: bool | None = None,
        mode: WafMode | None = None,
        custom_block_page: str | None = None,
        inherit_global_rules: bool | None = None,
        sqli_detection: bool | None = None,
        xss_detection: bool | None = None,
    ) -> WafConfigResponse:
        """Update WAF configuration for a zone.

        Args:
            zone_id: The zone ID.
            enabled: Enable or disable the WAF.
            mode: 'log_only' or 'blocking'.
            custom_block_page: Custom HTML for block page (None for default).
            inherit_global_rules: Inherit rules from global WAF config.
            sqli_detection: Enable SQL injection detection.
            xss_detection: Enable XSS detection.

        Returns:
            Updated WAF configuration.
        """
        data: dict[str, Any] = {}
        if enabled is not None:
            data["enabled"] = enabled
        if mode is not None:
            data["mode"] = mode.value
        if custom_block_page is not None:
            data["customBlockPage"] = custom_block_page
        if inherit_global_rules is not None:
            data["inheritGlobalRules"] = inherit_global_rules
        if sqli_detection is not None:
            data["sqliDetection"] = sqli_detection
        if xss_detection is not None:
            data["xssDetection"] = xss_detection

        response = self._put(f"/zones/{zone_id}/waf", data=data)
        return WafConfigResponse.model_validate(response.get("data", response))

    async def update_config_async(
        self,
        zone_id: str,
        enabled: bool | None = None,
        mode: WafMode | None = None,
        custom_block_page: str | None = None,
        inherit_global_rules: bool | None = None,
        sqli_detection: bool | None = None,
        xss_detection: bool | None = None,
    ) -> WafConfigResponse:
        """Update WAF configuration for a zone asynchronously.

        Args:
            zone_id: The zone ID.
            enabled: Enable or disable the WAF.
            mode: WAF mode.
            custom_block_page: Custom block page HTML.
            inherit_global_rules: Inherit global rules.
            sqli_detection: Enable SQLi detection.
            xss_detection: Enable XSS detection.

        Returns:
            Updated WAF configuration.
        """
        data: dict[str, Any] = {}
        if enabled is not None:
            data["enabled"] = enabled
        if mode is not None:
            data["mode"] = mode.value
        if custom_block_page is not None:
            data["customBlockPage"] = custom_block_page
        if inherit_global_rules is not None:
            data["inheritGlobalRules"] = inherit_global_rules
        if sqli_detection is not None:
            data["sqliDetection"] = sqli_detection
        if xss_detection is not None:
            data["xssDetection"] = xss_detection

        response = await self._put_async(f"/zones/{zone_id}/waf", data=data)
        return WafConfigResponse.model_validate(response.get("data", response))

    # ========================================================================
    # WAF Rules
    # ========================================================================

    def list_rules(
        self,
        zone_id: str,
        enabled: bool | None = None,
        rule_type: WafRuleType | None = None,
        sort_by: str = "priority",
        sort_order: str = "asc",
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[WafRule], PaginationMeta]:
        """List WAF rules for a zone.

        Args:
            zone_id: The zone ID.
            enabled: Filter by enabled status.
            rule_type: Filter by rule type.
            sort_by: Sort by 'priority', 'createdAt', or 'name'.
            sort_order: 'asc' or 'desc'.
            page: Page number.
            per_page: Items per page.

        Returns:
            Tuple of (list of rules, pagination metadata).
        """
        params: dict[str, Any] = {
            "sortBy": sort_by,
            "sortOrder": sort_order,
            "page": page,
            "perPage": per_page,
        }
        if enabled is not None:
            params["enabled"] = str(enabled).lower()
        if rule_type is not None:
            params["ruleType"] = rule_type.value

        response = self._get(f"/zones/{zone_id}/waf/rules", params=params)
        rules = [WafRule.model_validate(r) for r in response.get("data", [])]
        meta = PaginationMeta.model_validate(response.get("meta", {}))
        return rules, meta

    async def list_rules_async(
        self,
        zone_id: str,
        enabled: bool | None = None,
        rule_type: WafRuleType | None = None,
        sort_by: str = "priority",
        sort_order: str = "asc",
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[WafRule], PaginationMeta]:
        """List WAF rules for a zone asynchronously.

        Args:
            zone_id: The zone ID.
            enabled: Filter by enabled status.
            rule_type: Filter by rule type.
            sort_by: Sort field.
            sort_order: Sort order.
            page: Page number.
            per_page: Items per page.

        Returns:
            Tuple of (list of rules, pagination metadata).
        """
        params: dict[str, Any] = {
            "sortBy": sort_by,
            "sortOrder": sort_order,
            "page": page,
            "perPage": per_page,
        }
        if enabled is not None:
            params["enabled"] = str(enabled).lower()
        if rule_type is not None:
            params["ruleType"] = rule_type.value

        response = await self._get_async(f"/zones/{zone_id}/waf/rules", params=params)
        rules = [WafRule.model_validate(r) for r in response.get("data", [])]
        meta = PaginationMeta.model_validate(response.get("meta", {}))
        return rules, meta

    def get_rule(self, zone_id: str, rule_id: str) -> WafRule:
        """Get a specific WAF rule.

        Args:
            zone_id: The zone ID.
            rule_id: The rule ID.

        Returns:
            The WAF rule.
        """
        response = self._get(f"/zones/{zone_id}/waf/rules/{rule_id}")
        return WafRule.model_validate(response.get("data", response))

    async def get_rule_async(self, zone_id: str, rule_id: str) -> WafRule:
        """Get a specific WAF rule asynchronously.

        Args:
            zone_id: The zone ID.
            rule_id: The rule ID.

        Returns:
            The WAF rule.
        """
        response = await self._get_async(f"/zones/{zone_id}/waf/rules/{rule_id}")
        return WafRule.model_validate(response.get("data", response))

    def create_rule(
        self,
        zone_id: str,
        name: str,
        rule_type: WafRuleType,
        match_target: WafMatchTarget,
        match_pattern: str,
        action: WafAction,
        description: str | None = None,
        severity: WafSeverity = WafSeverity.MEDIUM,
        enabled: bool = True,
        priority: int = 500,
        metadata: dict[str, Any] | None = None,
    ) -> WafRule:
        """Create a WAF rule.

        Args:
            zone_id: The zone ID.
            name: Rule name (1-100 characters).
            rule_type: Rule type.
            match_target: What to match against.
            match_pattern: Regex or value pattern.
            action: Action to take.
            description: Rule description (max 500 characters).
            severity: Severity level.
            enabled: Enable the rule.
            priority: Execution order 0-10000 (lower = first).
            metadata: Additional metadata.

        Returns:
            The created rule.
        """
        data: dict[str, Any] = {
            "name": name,
            "ruleType": rule_type.value,
            "matchTarget": match_target.value,
            "matchPattern": match_pattern,
            "action": action.value,
            "severity": severity.value,
            "enabled": enabled,
            "priority": priority,
        }
        if description:
            data["description"] = description
        if metadata:
            data["metadata"] = metadata

        response = self._post(f"/zones/{zone_id}/waf/rules", data=data)
        return WafRule.model_validate(response.get("data", response))

    async def create_rule_async(
        self,
        zone_id: str,
        name: str,
        rule_type: WafRuleType,
        match_target: WafMatchTarget,
        match_pattern: str,
        action: WafAction,
        description: str | None = None,
        severity: WafSeverity = WafSeverity.MEDIUM,
        enabled: bool = True,
        priority: int = 500,
        metadata: dict[str, Any] | None = None,
    ) -> WafRule:
        """Create a WAF rule asynchronously.

        Args:
            zone_id: The zone ID.
            name: Rule name.
            rule_type: Rule type.
            match_target: Match target.
            match_pattern: Match pattern.
            action: Action.
            description: Description.
            severity: Severity.
            enabled: Enabled.
            priority: Priority.
            metadata: Metadata.

        Returns:
            The created rule.
        """
        data: dict[str, Any] = {
            "name": name,
            "ruleType": rule_type.value,
            "matchTarget": match_target.value,
            "matchPattern": match_pattern,
            "action": action.value,
            "severity": severity.value,
            "enabled": enabled,
            "priority": priority,
        }
        if description:
            data["description"] = description
        if metadata:
            data["metadata"] = metadata

        response = await self._post_async(f"/zones/{zone_id}/waf/rules", data=data)
        return WafRule.model_validate(response.get("data", response))

    def update_rule(
        self,
        zone_id: str,
        rule_id: str,
        name: str | None = None,
        description: str | None = None,
        match_pattern: str | None = None,
        action: WafAction | None = None,
        severity: WafSeverity | None = None,
        enabled: bool | None = None,
        priority: int | None = None,
    ) -> WafRule:
        """Update a WAF rule.

        Args:
            zone_id: The zone ID.
            rule_id: The rule ID.
            name: Rule name.
            description: Description.
            match_pattern: Match pattern.
            action: Action.
            severity: Severity.
            enabled: Enabled.
            priority: Priority.

        Returns:
            The updated rule.
        """
        data: dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if match_pattern is not None:
            data["matchPattern"] = match_pattern
        if action is not None:
            data["action"] = action.value
        if severity is not None:
            data["severity"] = severity.value
        if enabled is not None:
            data["enabled"] = enabled
        if priority is not None:
            data["priority"] = priority

        response = self._put(f"/zones/{zone_id}/waf/rules/{rule_id}", data=data)
        return WafRule.model_validate(response.get("data", response))

    async def update_rule_async(
        self,
        zone_id: str,
        rule_id: str,
        **kwargs: Any,
    ) -> WafRule:
        """Update a WAF rule asynchronously.

        Args:
            zone_id: The zone ID.
            rule_id: The rule ID.
            **kwargs: Rule fields to update.

        Returns:
            The updated rule.
        """
        data: dict[str, Any] = {}
        if kwargs.get("name") is not None:
            data["name"] = kwargs["name"]
        if kwargs.get("description") is not None:
            data["description"] = kwargs["description"]
        if kwargs.get("match_pattern") is not None:
            data["matchPattern"] = kwargs["match_pattern"]
        if kwargs.get("action") is not None:
            data["action"] = kwargs["action"].value
        if kwargs.get("severity") is not None:
            data["severity"] = kwargs["severity"].value
        if kwargs.get("enabled") is not None:
            data["enabled"] = kwargs["enabled"]
        if kwargs.get("priority") is not None:
            data["priority"] = kwargs["priority"]

        response = await self._put_async(
            f"/zones/{zone_id}/waf/rules/{rule_id}",
            data=data,
        )
        return WafRule.model_validate(response.get("data", response))

    def delete_rule(self, zone_id: str, rule_id: str) -> bool:
        """Delete a WAF rule.

        Args:
            zone_id: The zone ID.
            rule_id: The rule ID.

        Returns:
            True if successful.
        """
        response = self._delete(f"/zones/{zone_id}/waf/rules/{rule_id}")
        return cast(bool, response.get("success", True))

    async def delete_rule_async(self, zone_id: str, rule_id: str) -> bool:
        """Delete a WAF rule asynchronously.

        Args:
            zone_id: The zone ID.
            rule_id: The rule ID.

        Returns:
            True if successful.
        """
        response = await self._delete_async(f"/zones/{zone_id}/waf/rules/{rule_id}")
        return cast(bool, response.get("success", True))

    # ========================================================================
    # IP Lists
    # ========================================================================

    def list_ips(
        self,
        zone_id: str,
        list_type: IpListType | None = None,
        search: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[WafIpEntry], PaginationMeta]:
        """List IP entries for a zone's WAF.

        Args:
            zone_id: The zone ID.
            list_type: Filter by 'allow' or 'block'.
            search: Search by IP address.
            page: Page number.
            per_page: Items per page (max 100).

        Returns:
            Tuple of (list of IP entries, pagination metadata).
        """
        params: dict[str, Any] = {"page": page, "perPage": per_page}
        if list_type is not None:
            params["listType"] = list_type.value
        if search:
            params["search"] = search

        response = self._get(f"/zones/{zone_id}/waf/ip-lists", params=params)
        ips = [WafIpEntry.model_validate(i) for i in response.get("data", [])]
        meta = PaginationMeta.model_validate(response.get("meta", {}))
        return ips, meta

    async def list_ips_async(
        self,
        zone_id: str,
        list_type: IpListType | None = None,
        search: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[WafIpEntry], PaginationMeta]:
        """List IP entries for a zone's WAF asynchronously.

        Args:
            zone_id: The zone ID.
            list_type: Filter by list type.
            search: Search by IP.
            page: Page number.
            per_page: Items per page.

        Returns:
            Tuple of (list of IP entries, pagination metadata).
        """
        params: dict[str, Any] = {"page": page, "perPage": per_page}
        if list_type is not None:
            params["listType"] = list_type.value
        if search:
            params["search"] = search

        response = await self._get_async(
            f"/zones/{zone_id}/waf/ip-lists",
            params=params,
        )
        ips = [WafIpEntry.model_validate(i) for i in response.get("data", [])]
        meta = PaginationMeta.model_validate(response.get("meta", {}))
        return ips, meta

    def add_ip(
        self,
        zone_id: str,
        list_type: IpListType,
        ip_address: str,
        reason: str | None = None,
        expires_at: datetime | None = None,
    ) -> WafIpEntry:
        """Add an IP address to the allow or block list.

        Args:
            zone_id: The zone ID.
            list_type: 'allow' or 'block'.
            ip_address: IP address or CIDR range.
            reason: Reason for adding (max 500 characters).
            expires_at: Expiration datetime.

        Returns:
            The created IP entry.
        """
        data: dict[str, Any] = {
            "listType": list_type.value,
            "ipAddress": ip_address,
        }
        if reason:
            data["reason"] = reason
        if expires_at:
            data["expiresAt"] = expires_at.isoformat()

        response = self._post(f"/zones/{zone_id}/waf/ip-lists", data=data)
        return WafIpEntry.model_validate(response.get("data", response))

    async def add_ip_async(
        self,
        zone_id: str,
        list_type: IpListType,
        ip_address: str,
        reason: str | None = None,
        expires_at: datetime | None = None,
    ) -> WafIpEntry:
        """Add an IP address to the allow or block list asynchronously.

        Args:
            zone_id: The zone ID.
            list_type: List type.
            ip_address: IP address or CIDR.
            reason: Reason.
            expires_at: Expiration.

        Returns:
            The created IP entry.
        """
        data: dict[str, Any] = {
            "listType": list_type.value,
            "ipAddress": ip_address,
        }
        if reason:
            data["reason"] = reason
        if expires_at:
            data["expiresAt"] = expires_at.isoformat()

        response = await self._post_async(f"/zones/{zone_id}/waf/ip-lists", data=data)
        return WafIpEntry.model_validate(response.get("data", response))

    def block_ip(
        self,
        zone_id: str,
        ip_address: str,
        reason: str | None = None,
        expires_at: datetime | None = None,
    ) -> WafIpEntry:
        """Block an IP address.

        Args:
            zone_id: The zone ID.
            ip_address: IP address or CIDR range.
            reason: Reason for blocking.
            expires_at: Expiration datetime.

        Returns:
            The created IP entry.
        """
        return self.add_ip(zone_id, IpListType.BLOCK, ip_address, reason, expires_at)

    def allow_ip(
        self,
        zone_id: str,
        ip_address: str,
        reason: str | None = None,
    ) -> WafIpEntry:
        """Whitelist an IP address.

        Args:
            zone_id: The zone ID.
            ip_address: IP address or CIDR range.
            reason: Reason for allowing.

        Returns:
            The created IP entry.
        """
        return self.add_ip(zone_id, IpListType.ALLOW, ip_address, reason)

    def update_ip(
        self,
        zone_id: str,
        ip_id: str,
        reason: str | None = None,
        expires_at: datetime | None = None,
    ) -> WafIpEntry:
        """Update an IP list entry.

        Args:
            zone_id: The zone ID.
            ip_id: The IP entry ID.
            reason: Updated reason.
            expires_at: Updated expiration (None to remove).

        Returns:
            The updated IP entry.
        """
        data: dict[str, Any] = {}
        if reason is not None:
            data["reason"] = reason
        if expires_at is not None:
            data["expiresAt"] = expires_at.isoformat()
        elif "expires_at" in locals():
            data["expiresAt"] = None

        response = self._put(f"/zones/{zone_id}/waf/ip-lists/{ip_id}", data=data)
        return WafIpEntry.model_validate(response.get("data", response))

    async def update_ip_async(
        self,
        zone_id: str,
        ip_id: str,
        reason: str | None = None,
        expires_at: datetime | None = None,
    ) -> WafIpEntry:
        """Update an IP list entry asynchronously.

        Args:
            zone_id: The zone ID.
            ip_id: The IP entry ID.
            reason: Updated reason.
            expires_at: Updated expiration.

        Returns:
            The updated IP entry.
        """
        data: dict[str, Any] = {}
        if reason is not None:
            data["reason"] = reason
        if expires_at is not None:
            data["expiresAt"] = expires_at.isoformat()

        response = await self._put_async(
            f"/zones/{zone_id}/waf/ip-lists/{ip_id}",
            data=data,
        )
        return WafIpEntry.model_validate(response.get("data", response))

    def delete_ip(self, zone_id: str, ip_id: str) -> bool:
        """Remove an IP from the list.

        Args:
            zone_id: The zone ID.
            ip_id: The IP entry ID.

        Returns:
            True if successful.
        """
        response = self._delete(f"/zones/{zone_id}/waf/ip-lists/{ip_id}")
        return cast(bool, response.get("success", True))

    async def delete_ip_async(self, zone_id: str, ip_id: str) -> bool:
        """Remove an IP from the list asynchronously.

        Args:
            zone_id: The zone ID.
            ip_id: The IP entry ID.

        Returns:
            True if successful.
        """
        response = await self._delete_async(f"/zones/{zone_id}/waf/ip-lists/{ip_id}")
        return cast(bool, response.get("success", True))

    # ========================================================================
    # Country Rules
    # ========================================================================

    def list_countries(self, zone_id: str) -> list[WafCountryRule]:
        """List country blocking rules for a zone.

        Args:
            zone_id: The zone ID.

        Returns:
            List of country rules.
        """
        response = self._get(f"/zones/{zone_id}/waf/countries")
        return [WafCountryRule.model_validate(c) for c in response.get("data", [])]

    async def list_countries_async(self, zone_id: str) -> list[WafCountryRule]:
        """List country blocking rules for a zone asynchronously.

        Args:
            zone_id: The zone ID.

        Returns:
            List of country rules.
        """
        response = await self._get_async(f"/zones/{zone_id}/waf/countries")
        return [WafCountryRule.model_validate(c) for c in response.get("data", [])]

    def add_country(
        self,
        zone_id: str,
        country_code: str,
        action: WafAction,
        reason: str | None = None,
        enabled: bool = True,
    ) -> WafCountryRule:
        """Add a country blocking rule.

        Args:
            zone_id: The zone ID.
            country_code: ISO 3166-1 alpha-2 country code.
            action: 'block', 'challenge', or 'log'.
            reason: Reason for the rule (max 500 characters).
            enabled: Enable the rule.

        Returns:
            The created country rule.
        """
        data: dict[str, Any] = {
            "countryCode": country_code,
            "action": action.value,
            "enabled": enabled,
        }
        if reason:
            data["reason"] = reason

        response = self._post(f"/zones/{zone_id}/waf/countries", data=data)
        return WafCountryRule.model_validate(response.get("data", response))

    async def add_country_async(
        self,
        zone_id: str,
        country_code: str,
        action: WafAction,
        reason: str | None = None,
        enabled: bool = True,
    ) -> WafCountryRule:
        """Add a country blocking rule asynchronously.

        Args:
            zone_id: The zone ID.
            country_code: Country code.
            action: Action.
            reason: Reason.
            enabled: Enabled.

        Returns:
            The created country rule.
        """
        data: dict[str, Any] = {
            "countryCode": country_code,
            "action": action.value,
            "enabled": enabled,
        }
        if reason:
            data["reason"] = reason

        response = await self._post_async(f"/zones/{zone_id}/waf/countries", data=data)
        return WafCountryRule.model_validate(response.get("data", response))

    def update_country(
        self,
        zone_id: str,
        country_id: str,
        action: WafAction | None = None,
        reason: str | None = None,
        enabled: bool | None = None,
    ) -> WafCountryRule:
        """Update a country rule.

        Args:
            zone_id: The zone ID.
            country_id: The country rule ID.
            action: Action.
            reason: Reason.
            enabled: Enabled.

        Returns:
            The updated country rule.
        """
        data: dict[str, Any] = {}
        if action is not None:
            data["action"] = action.value
        if reason is not None:
            data["reason"] = reason
        if enabled is not None:
            data["enabled"] = enabled

        response = self._put(
            f"/zones/{zone_id}/waf/countries/{country_id}",
            data=data,
        )
        return WafCountryRule.model_validate(response.get("data", response))

    async def update_country_async(
        self,
        zone_id: str,
        country_id: str,
        action: WafAction | None = None,
        reason: str | None = None,
        enabled: bool | None = None,
    ) -> WafCountryRule:
        """Update a country rule asynchronously.

        Args:
            zone_id: The zone ID.
            country_id: The country rule ID.
            action: Action.
            reason: Reason.
            enabled: Enabled.

        Returns:
            The updated country rule.
        """
        data: dict[str, Any] = {}
        if action is not None:
            data["action"] = action.value
        if reason is not None:
            data["reason"] = reason
        if enabled is not None:
            data["enabled"] = enabled

        response = await self._put_async(
            f"/zones/{zone_id}/waf/countries/{country_id}",
            data=data,
        )
        return WafCountryRule.model_validate(response.get("data", response))

    def delete_country(self, zone_id: str, country_id: str) -> bool:
        """Delete a country rule.

        Args:
            zone_id: The zone ID.
            country_id: The country rule ID.

        Returns:
            True if successful.
        """
        response = self._delete(f"/zones/{zone_id}/waf/countries/{country_id}")
        return cast(bool, response.get("success", True))

    async def delete_country_async(self, zone_id: str, country_id: str) -> bool:
        """Delete a country rule asynchronously.

        Args:
            zone_id: The zone ID.
            country_id: The country rule ID.

        Returns:
            True if successful.
        """
        response = await self._delete_async(
            f"/zones/{zone_id}/waf/countries/{country_id}"
        )
        return cast(bool, response.get("success", True))

    # ========================================================================
    # ASN Rules
    # ========================================================================

    def list_asns(self, zone_id: str) -> list[WafAsnRule]:
        """List ASN blocking rules for a zone.

        Args:
            zone_id: The zone ID.

        Returns:
            List of ASN rules.
        """
        response = self._get(f"/zones/{zone_id}/waf/asn")
        return [WafAsnRule.model_validate(a) for a in response.get("data", [])]

    async def list_asns_async(self, zone_id: str) -> list[WafAsnRule]:
        """List ASN blocking rules for a zone asynchronously.

        Args:
            zone_id: The zone ID.

        Returns:
            List of ASN rules.
        """
        response = await self._get_async(f"/zones/{zone_id}/waf/asn")
        return [WafAsnRule.model_validate(a) for a in response.get("data", [])]

    def add_asn(
        self,
        zone_id: str,
        asn: int,
        action: WafAction,
        asn_name: str | None = None,
        reason: str | None = None,
        enabled: bool = True,
    ) -> WafAsnRule:
        """Add an ASN blocking rule.

        Args:
            zone_id: The zone ID.
            asn: Autonomous System Number.
            action: 'block', 'challenge', or 'log'.
            asn_name: Human-readable ASN name (max 100 characters).
            reason: Reason for the rule (max 500 characters).
            enabled: Enable the rule.

        Returns:
            The created ASN rule.
        """
        data: dict[str, Any] = {
            "asn": asn,
            "action": action.value,
            "enabled": enabled,
        }
        if asn_name:
            data["asnName"] = asn_name
        if reason:
            data["reason"] = reason

        response = self._post(f"/zones/{zone_id}/waf/asn", data=data)
        return WafAsnRule.model_validate(response.get("data", response))

    async def add_asn_async(
        self,
        zone_id: str,
        asn: int,
        action: WafAction,
        asn_name: str | None = None,
        reason: str | None = None,
        enabled: bool = True,
    ) -> WafAsnRule:
        """Add an ASN blocking rule asynchronously.

        Args:
            zone_id: The zone ID.
            asn: ASN.
            action: Action.
            asn_name: ASN name.
            reason: Reason.
            enabled: Enabled.

        Returns:
            The created ASN rule.
        """
        data: dict[str, Any] = {
            "asn": asn,
            "action": action.value,
            "enabled": enabled,
        }
        if asn_name:
            data["asnName"] = asn_name
        if reason:
            data["reason"] = reason

        response = await self._post_async(f"/zones/{zone_id}/waf/asn", data=data)
        return WafAsnRule.model_validate(response.get("data", response))

    def update_asn(
        self,
        zone_id: str,
        asn_id: str,
        asn_name: str | None = None,
        action: WafAction | None = None,
        reason: str | None = None,
        enabled: bool | None = None,
    ) -> WafAsnRule:
        """Update an ASN rule.

        Args:
            zone_id: The zone ID.
            asn_id: The ASN rule ID.
            asn_name: ASN name.
            action: Action.
            reason: Reason.
            enabled: Enabled.

        Returns:
            The updated ASN rule.
        """
        data: dict[str, Any] = {}
        if asn_name is not None:
            data["asnName"] = asn_name
        if action is not None:
            data["action"] = action.value
        if reason is not None:
            data["reason"] = reason
        if enabled is not None:
            data["enabled"] = enabled

        response = self._put(f"/zones/{zone_id}/waf/asn/{asn_id}", data=data)
        return WafAsnRule.model_validate(response.get("data", response))

    async def update_asn_async(
        self,
        zone_id: str,
        asn_id: str,
        asn_name: str | None = None,
        action: WafAction | None = None,
        reason: str | None = None,
        enabled: bool | None = None,
    ) -> WafAsnRule:
        """Update an ASN rule asynchronously.

        Args:
            zone_id: The zone ID.
            asn_id: The ASN rule ID.
            asn_name: ASN name.
            action: Action.
            reason: Reason.
            enabled: Enabled.

        Returns:
            The updated ASN rule.
        """
        data: dict[str, Any] = {}
        if asn_name is not None:
            data["asnName"] = asn_name
        if action is not None:
            data["action"] = action.value
        if reason is not None:
            data["reason"] = reason
        if enabled is not None:
            data["enabled"] = enabled

        response = await self._put_async(
            f"/zones/{zone_id}/waf/asn/{asn_id}",
            data=data,
        )
        return WafAsnRule.model_validate(response.get("data", response))

    def delete_asn(self, zone_id: str, asn_id: str) -> bool:
        """Delete an ASN rule.

        Args:
            zone_id: The zone ID.
            asn_id: The ASN rule ID.

        Returns:
            True if successful.
        """
        response = self._delete(f"/zones/{zone_id}/waf/asn/{asn_id}")
        return cast(bool, response.get("success", True))

    async def delete_asn_async(self, zone_id: str, asn_id: str) -> bool:
        """Delete an ASN rule asynchronously.

        Args:
            zone_id: The zone ID.
            asn_id: The ASN rule ID.

        Returns:
            True if successful.
        """
        response = await self._delete_async(f"/zones/{zone_id}/waf/asn/{asn_id}")
        return cast(bool, response.get("success", True))
