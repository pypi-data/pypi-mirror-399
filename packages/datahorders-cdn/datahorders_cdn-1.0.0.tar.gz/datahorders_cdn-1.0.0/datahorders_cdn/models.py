"""Pydantic models for the DataHorders CDN SDK."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

# ============================================================================
# Enums
# ============================================================================


class CertificateStatus(str, Enum):
    """Certificate status values."""

    PENDING = "pending"
    ACTIVE = "active"
    FAILED = "failed"
    EXPIRED = "expired"
    ERROR = "error"


class CertificateProvider(str, Enum):
    """Certificate provider types."""

    MANUAL = "manual"
    ACME = "acme"


class AcmeProvider(str, Enum):
    """ACME certificate providers."""

    LETSENCRYPT = "letsencrypt"
    ZEROSSL = "zerossl"
    GOOGLE = "google"


class LoadBalanceMethod(str, Enum):
    """Load balancing methods for upstream servers."""

    ROUND_ROBIN = "round_robin"
    LEAST_CONN = "least_conn"
    IP_HASH = "ip_hash"


class ServerProtocol(str, Enum):
    """Protocol for upstream servers."""

    HTTP = "http"
    HTTPS = "https"


class WafMode(str, Enum):
    """WAF operation modes."""

    LOG_ONLY = "log_only"
    BLOCKING = "blocking"


class WafRuleType(str, Enum):
    """WAF rule types."""

    PATTERN = "pattern"
    IP_ALLOW = "ip_allow"
    IP_BLOCK = "ip_block"
    COUNTRY = "country"
    ASN = "asn"
    SQLI = "sqli"
    XSS = "xss"
    RATE_LIMIT = "rate_limit"


class WafMatchTarget(str, Enum):
    """WAF rule match targets."""

    URI = "uri"
    QUERY = "query"
    HEADERS = "headers"
    BODY = "body"
    COOKIES = "cookies"
    USER_AGENT = "user_agent"
    IP = "ip"
    COUNTRY = "country"
    ASN = "asn"
    METHOD = "method"


class WafAction(str, Enum):
    """WAF rule actions."""

    ALLOW = "allow"
    BLOCK = "block"
    LOG = "log"
    CHALLENGE = "challenge"
    RATE_LIMIT = "rate_limit"
    TARPIT = "tarpit"


class WafSeverity(str, Enum):
    """WAF rule severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IpListType(str, Enum):
    """IP list types (allow/block)."""

    ALLOW = "allow"
    BLOCK = "block"


class HealthCheckProtocol(str, Enum):
    """Health check protocols."""

    HTTP = "http"
    HTTPS = "https"
    TCP = "tcp"


class HealthCheckMethod(str, Enum):
    """Health check HTTP methods."""

    HEAD = "HEAD"
    GET = "GET"
    POST = "POST"


# ============================================================================
# Base Models
# ============================================================================


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int
    per_page: int = Field(alias="perPage")
    total: int
    total_pages: int = Field(alias="totalPages")

    class Config:
        """Pydantic config."""

        populate_by_name = True


class ApiResponse(BaseModel):
    """Generic API response wrapper."""

    success: bool
    data: Any = None
    error: Any = None
    meta: Optional[PaginationMeta] = None


# ============================================================================
# Domain Models
# ============================================================================


class ZoneReference(BaseModel):
    """Reference to a zone in domain responses."""

    id: str
    name: str


class DomainZone(BaseModel):
    """Zone association for a domain."""

    zone: ZoneReference


class Domain(BaseModel):
    """Domain model."""

    id: str
    domain: str
    verified: bool
    health_check_enabled: bool = Field(alias="healthCheckEnabled")
    user_id: str = Field(alias="userId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    zones: list[DomainZone] = Field(default_factory=list)

    class Config:
        """Pydantic config."""

        populate_by_name = True


class DomainVerification(BaseModel):
    """Domain verification information."""

    code: str
    instructions: str


class DomainCreateResponse(BaseModel):
    """Response from creating a domain."""

    domain: Domain
    verification: DomainVerification


class DomainVerifyResponse(BaseModel):
    """Response from verifying a domain."""

    verified: bool
    message: str


class DomainDeleteResponse(BaseModel):
    """Response from deleting a domain."""

    id: str
    deleted: bool


# ============================================================================
# Certificate Models
# ============================================================================


class CertificateDomain(BaseModel):
    """Domain associated with a certificate."""

    domain: str


class Certificate(BaseModel):
    """Certificate model."""

    id: str
    name: str
    provider: CertificateProvider
    acme_provider: Optional[AcmeProvider] = Field(default=None, alias="acmeProvider")
    status: CertificateStatus
    auto_renew: bool = Field(alias="autoRenew")
    is_wildcard: bool = Field(default=False, alias="isWildcard")
    email: Optional[str] = None
    expires_at: Optional[datetime] = Field(default=None, alias="expiresAt")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    domains: list[CertificateDomain] = Field(default_factory=list)

    class Config:
        """Pydantic config."""

        populate_by_name = True


class AcmeCertificateStatus(BaseModel):
    """ACME certificate status response."""

    certificate_id: str = Field(alias="certificateId")
    name: Optional[str] = None
    status: CertificateStatus
    progress: int
    message: str
    domains: list[str] = Field(default_factory=list)
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    expires_at: Optional[datetime] = Field(default=None, alias="expiresAt")

    class Config:
        """Pydantic config."""

        populate_by_name = True


class CertificateDeleteResponse(BaseModel):
    """Response from deleting a certificate."""

    domain: str
    deleted: bool


# ============================================================================
# Upstream Server Models
# ============================================================================


class UpstreamServer(BaseModel):
    """Upstream server model."""

    id: str
    name: Optional[str] = None
    address: str
    port: int
    protocol: ServerProtocol = ServerProtocol.HTTP
    weight: int = 1
    backup: bool = False
    health_check_path: Optional[str] = Field(default=None, alias="healthCheckPath")
    health_check_connect_timeout: Optional[int] = Field(
        default=None, alias="healthCheckConnectTimeout"
    )
    health_check_timeout: Optional[int] = Field(
        default=None, alias="healthCheckTimeout"
    )
    health_check_retries: Optional[int] = Field(
        default=None, alias="healthCheckRetries"
    )
    region: Optional[str] = None
    country: Optional[str] = None
    upstream_id: Optional[str] = Field(default=None, alias="upstreamId")

    class Config:
        """Pydantic config."""

        populate_by_name = True


class Upstream(BaseModel):
    """Upstream configuration model."""

    id: str
    name: Optional[str] = None
    load_balance_method: LoadBalanceMethod = Field(
        default=LoadBalanceMethod.ROUND_ROBIN, alias="loadBalanceMethod"
    )
    servers: list[UpstreamServer] = Field(default_factory=list)

    class Config:
        """Pydantic config."""

        populate_by_name = True


# ============================================================================
# Zone Models
# ============================================================================


class ZoneDomainInfo(BaseModel):
    """Domain info within a zone."""

    id: str
    domain: str
    verified: bool


class ZoneDomain(BaseModel):
    """Domain association in a zone."""

    domain_id: str = Field(alias="domainId")
    is_primary: bool = Field(alias="isPrimary")
    domain: ZoneDomainInfo

    class Config:
        """Pydantic config."""

        populate_by_name = True


class ZoneCertificateDomain(BaseModel):
    """Domain in zone certificate."""

    domain: str


class ZoneCertificate(BaseModel):
    """Certificate info in a zone."""

    id: str
    name: str
    provider: CertificateProvider
    status: CertificateStatus
    expires_at: Optional[datetime] = Field(default=None, alias="expiresAt")
    domains: list[ZoneCertificateDomain] = Field(default_factory=list)

    class Config:
        """Pydantic config."""

        populate_by_name = True


class HealthStatus(BaseModel):
    """Health status summary."""

    healthy: int
    unhealthy: int
    disabled: int
    total: int


class Zone(BaseModel):
    """Zone model."""

    id: str
    name: str
    upgrade_insecure: bool = Field(alias="upgradeInsecure")
    four_k_fallback: bool = Field(alias="fourKFallback")
    health_check_enabled: bool = Field(alias="healthCheckEnabled")
    user_id: str = Field(alias="userId")
    certificate_id: Optional[str] = Field(default=None, alias="certificateId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    deleted_at: Optional[datetime] = Field(default=None, alias="deletedAt")
    domains: list[ZoneDomain] = Field(default_factory=list)
    upstream: Optional[Upstream] = None
    certificate: Optional[ZoneCertificate] = None
    health_status: Optional[HealthStatus] = Field(default=None, alias="healthStatus")

    class Config:
        """Pydantic config."""

        populate_by_name = True


class ZoneDeleteResponse(BaseModel):
    """Response from deleting a zone."""

    id: str
    deleted: bool
    message: Optional[str] = None


# ============================================================================
# Health Check Models
# ============================================================================


class HealthCheckProfile(BaseModel):
    """Health check profile model."""

    id: str
    name: str
    description: Optional[str] = None
    protocol: HealthCheckProtocol = HealthCheckProtocol.HTTP
    port: int = 80
    path: str = "/"
    method: HealthCheckMethod = HealthCheckMethod.HEAD
    expected_status_codes: str = Field(default="200-399", alias="expectedStatusCodes")
    expected_response_text: Optional[str] = Field(
        default=None, alias="expectedResponseText"
    )
    check_interval: int = Field(default=30, alias="checkInterval")
    timeout: int = 10
    retries: int = 2
    follow_redirects: bool = Field(default=False, alias="followRedirects")
    verify_ssl: bool = Field(default=False, alias="verifySSL")
    custom_headers: Optional[dict[str, str]] = Field(
        default=None, alias="customHeaders"
    )
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")
    created_by: Optional[str] = Field(default=None, alias="createdBy")
    server_count: Optional[int] = Field(default=None, alias="serverCount")

    class Config:
        """Pydantic config."""

        populate_by_name = True


class CdnNode(BaseModel):
    """CDN edge node model."""

    id: str
    domain: str
    ip_address: str = Field(alias="ipAddress")
    type: str
    port: int
    resource_path: str = Field(alias="resourcePath")

    class Config:
        """Pydantic config."""

        populate_by_name = True


class HealthCheckToggleResponse(BaseModel):
    """Response from toggling health checks."""

    success: bool
    message: str
    server_id: str = Field(alias="serverId")
    action: str
    reason: Optional[str] = None

    class Config:
        """Pydantic config."""

        populate_by_name = True


# ============================================================================
# WAF Models
# ============================================================================


class WafRule(BaseModel):
    """WAF rule model."""

    id: str
    zone_config_id: Optional[str] = Field(default=None, alias="zoneConfigId")
    name: str
    description: Optional[str] = None
    rule_type: WafRuleType = Field(alias="ruleType")
    match_target: WafMatchTarget = Field(alias="matchTarget")
    match_pattern: str = Field(alias="matchPattern")
    action: WafAction
    severity: WafSeverity = WafSeverity.MEDIUM
    enabled: bool = True
    priority: int = 500
    metadata: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")

    class Config:
        """Pydantic config."""

        populate_by_name = True


class WafIpEntry(BaseModel):
    """WAF IP list entry model."""

    id: str
    zone_config_id: Optional[str] = Field(default=None, alias="zoneConfigId")
    list_type: IpListType = Field(alias="listType")
    ip_address: str = Field(alias="ipAddress")
    reason: Optional[str] = None
    expires_at: Optional[datetime] = Field(default=None, alias="expiresAt")
    created_by: Optional[str] = Field(default=None, alias="createdBy")
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")

    class Config:
        """Pydantic config."""

        populate_by_name = True


class WafCountryRule(BaseModel):
    """WAF country blocking rule model."""

    id: str
    zone_config_id: Optional[str] = Field(default=None, alias="zoneConfigId")
    country_code: str = Field(alias="countryCode")
    action: WafAction
    reason: Optional[str] = None
    enabled: bool = True
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")

    class Config:
        """Pydantic config."""

        populate_by_name = True


class WafAsnRule(BaseModel):
    """WAF ASN blocking rule model."""

    id: str
    zone_config_id: Optional[str] = Field(default=None, alias="zoneConfigId")
    asn: int
    asn_name: Optional[str] = Field(default=None, alias="asnName")
    action: WafAction
    reason: Optional[str] = None
    enabled: bool = True
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")

    class Config:
        """Pydantic config."""

        populate_by_name = True


class WafStats(BaseModel):
    """WAF statistics."""

    total_rules: int = Field(alias="totalRules")
    active_rules: int = Field(alias="activeRules")
    blocked_ips: int = Field(alias="blockedIps")
    allowed_ips: int = Field(alias="allowedIps")
    country_rules: int = Field(alias="countryRules")
    asn_rules: int = Field(alias="asnRules")

    class Config:
        """Pydantic config."""

        populate_by_name = True


class WafConfig(BaseModel):
    """WAF configuration model."""

    id: str
    zone_id: str = Field(alias="zoneId")
    enabled: bool = True
    mode: WafMode = WafMode.LOG_ONLY
    custom_block_page: Optional[str] = Field(default=None, alias="customBlockPage")
    inherit_global_rules: bool = Field(default=True, alias="inheritGlobalRules")
    sqli_detection: bool = Field(default=True, alias="sqliDetection")
    xss_detection: bool = Field(default=True, alias="xssDetection")
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")
    zone_rules: list[WafRule] = Field(default_factory=list, alias="zoneRules")
    ip_lists: list[WafIpEntry] = Field(default_factory=list, alias="ipLists")
    country_rules: list[WafCountryRule] = Field(
        default_factory=list, alias="countryRules"
    )
    asn_rules: list[WafAsnRule] = Field(default_factory=list, alias="asnRules")

    class Config:
        """Pydantic config."""

        populate_by_name = True


class WafConfigResponse(BaseModel):
    """WAF configuration API response."""

    config: WafConfig
    stats: WafStats


# ============================================================================
# Analytics Models
# ============================================================================


class ZoneUsage(BaseModel):
    """Per-zone usage statistics."""

    zone: str
    gigabytes_sent: float
    requests: int


class DateRange(BaseModel):
    """Date range for analytics."""

    start: datetime
    end: datetime


class TotalTraffic(BaseModel):
    """Total traffic statistics."""

    gigabytes: float


class UsageMetrics(BaseModel):
    """Usage metrics response."""

    total_traffic: TotalTraffic
    total_zones: int
    zones: list[ZoneUsage]
    date_range: DateRange


# ============================================================================
# Request Models (for creating/updating resources)
# ============================================================================


class DomainCreateRequest(BaseModel):
    """Request to create a domain."""

    domain: str
    health_check_enabled: bool = Field(default=False, alias="healthCheckEnabled")

    class Config:
        """Pydantic config."""

        populate_by_name = True


class DomainVerifyRequest(BaseModel):
    """Request to verify a domain."""

    domain: Optional[str] = None
    id: Optional[str] = None


class UpstreamServerCreate(BaseModel):
    """Server configuration for creating upstream."""

    name: Optional[str] = None
    address: str
    port: int = 80
    protocol: ServerProtocol = ServerProtocol.HTTP
    weight: int = 1
    backup: bool = False
    health_check_path: Optional[str] = Field(default=None, alias="healthCheckPath")

    class Config:
        """Pydantic config."""

        populate_by_name = True


class UpstreamCreate(BaseModel):
    """Upstream configuration for zone creation."""

    load_balance_method: LoadBalanceMethod = Field(
        default=LoadBalanceMethod.ROUND_ROBIN, alias="loadBalanceMethod"
    )
    servers: list[UpstreamServerCreate]

    class Config:
        """Pydantic config."""

        populate_by_name = True


class ZoneCreateRequest(BaseModel):
    """Request to create a zone."""

    name: str
    domains: list[str]
    certificate_id: Optional[str] = Field(default=None, alias="certificateId")
    upgrade_insecure: bool = Field(default=True, alias="upgradeInsecure")
    four_k_fallback: bool = Field(default=False, alias="fourKFallback")
    health_check_enabled: bool = Field(default=False, alias="healthCheckEnabled")
    upstream: UpstreamCreate

    class Config:
        """Pydantic config."""

        populate_by_name = True


class ZoneUpdateRequest(BaseModel):
    """Request to update a zone."""

    name: Optional[str] = None
    domains: Optional[list[str]] = None
    certificate_id: Optional[str] = Field(default=None, alias="certificateId")
    force_certificate_removal: bool = Field(
        default=False, alias="forceCertificateRemoval"
    )
    upgrade_insecure: Optional[bool] = Field(default=None, alias="upgradeInsecure")
    four_k_fallback: Optional[bool] = Field(default=None, alias="fourKFallback")
    health_check_enabled: Optional[bool] = Field(
        default=None, alias="healthCheckEnabled"
    )
    upstream: Optional[UpstreamCreate] = None

    class Config:
        """Pydantic config."""

        populate_by_name = True


class CertificateCreateRequest(BaseModel):
    """Request to create a manual certificate."""

    name: str
    provider: CertificateProvider = CertificateProvider.MANUAL
    domains: Optional[list[str]] = None
    cert_content: str = Field(alias="certContent")
    key_content: str = Field(alias="keyContent")
    auto_renew: bool = Field(default=False, alias="autoRenew")
    force: bool = False

    class Config:
        """Pydantic config."""

        populate_by_name = True


class AcmeCertificateCreateRequest(BaseModel):
    """Request to create an ACME certificate."""

    name: str
    domains: list[str]
    email: str
    acme_provider: AcmeProvider = Field(
        default=AcmeProvider.LETSENCRYPT, alias="acmeProvider"
    )
    auto_renew: bool = Field(default=True, alias="autoRenew")
    force: bool = False

    class Config:
        """Pydantic config."""

        populate_by_name = True


class CertificateUpdateRequest(BaseModel):
    """Request to update a certificate."""

    name: Optional[str] = None
    auto_renew: Optional[bool] = Field(default=None, alias="autoRenew")
    cert_content: Optional[str] = Field(default=None, alias="certContent")
    key_content: Optional[str] = Field(default=None, alias="keyContent")

    class Config:
        """Pydantic config."""

        populate_by_name = True


class HealthCheckProfileCreateRequest(BaseModel):
    """Request to create a health check profile."""

    name: str
    description: Optional[str] = None
    protocol: HealthCheckProtocol = HealthCheckProtocol.HTTP
    port: int = 80
    path: str = "/"
    method: HealthCheckMethod = HealthCheckMethod.HEAD
    expected_status_codes: str = Field(default="200-399", alias="expectedStatusCodes")
    expected_response_text: Optional[str] = Field(
        default=None, alias="expectedResponseText"
    )
    check_interval: int = Field(default=30, alias="checkInterval")
    timeout: int = 10
    retries: int = 2
    follow_redirects: bool = Field(default=False, alias="followRedirects")
    verify_ssl: bool = Field(default=False, alias="verifySSL")
    custom_headers: Optional[dict[str, str]] = Field(
        default=None, alias="customHeaders"
    )

    class Config:
        """Pydantic config."""

        populate_by_name = True


class WafConfigUpdateRequest(BaseModel):
    """Request to update WAF configuration."""

    enabled: Optional[bool] = None
    mode: Optional[WafMode] = None
    custom_block_page: Optional[str] = Field(default=None, alias="customBlockPage")
    inherit_global_rules: Optional[bool] = Field(
        default=None, alias="inheritGlobalRules"
    )
    sqli_detection: Optional[bool] = Field(default=None, alias="sqliDetection")
    xss_detection: Optional[bool] = Field(default=None, alias="xssDetection")

    class Config:
        """Pydantic config."""

        populate_by_name = True


class WafRuleCreateRequest(BaseModel):
    """Request to create a WAF rule."""

    name: str
    description: Optional[str] = None
    rule_type: WafRuleType = Field(alias="ruleType")
    match_target: WafMatchTarget = Field(alias="matchTarget")
    match_pattern: str = Field(alias="matchPattern")
    action: WafAction
    severity: WafSeverity = WafSeverity.MEDIUM
    enabled: bool = True
    priority: int = 500
    metadata: Optional[dict[str, Any]] = None

    class Config:
        """Pydantic config."""

        populate_by_name = True


class WafRuleUpdateRequest(BaseModel):
    """Request to update a WAF rule."""

    name: Optional[str] = None
    description: Optional[str] = None
    match_pattern: Optional[str] = Field(default=None, alias="matchPattern")
    action: Optional[WafAction] = None
    severity: Optional[WafSeverity] = None
    enabled: Optional[bool] = None
    priority: Optional[int] = None

    class Config:
        """Pydantic config."""

        populate_by_name = True


class WafIpCreateRequest(BaseModel):
    """Request to add an IP to the WAF list."""

    list_type: IpListType = Field(alias="listType")
    ip_address: str = Field(alias="ipAddress")
    reason: Optional[str] = None
    expires_at: Optional[datetime] = Field(default=None, alias="expiresAt")

    class Config:
        """Pydantic config."""

        populate_by_name = True


class WafIpUpdateRequest(BaseModel):
    """Request to update a WAF IP entry."""

    reason: Optional[str] = None
    expires_at: Optional[datetime] = Field(default=None, alias="expiresAt")

    class Config:
        """Pydantic config."""

        populate_by_name = True


class WafCountryCreateRequest(BaseModel):
    """Request to create a country rule."""

    country_code: str = Field(alias="countryCode")
    action: WafAction
    reason: Optional[str] = None
    enabled: bool = True

    class Config:
        """Pydantic config."""

        populate_by_name = True


class WafCountryUpdateRequest(BaseModel):
    """Request to update a country rule."""

    action: Optional[WafAction] = None
    reason: Optional[str] = None
    enabled: Optional[bool] = None

    class Config:
        """Pydantic config."""

        populate_by_name = True


class WafAsnCreateRequest(BaseModel):
    """Request to create an ASN rule."""

    asn: int
    asn_name: Optional[str] = Field(default=None, alias="asnName")
    action: WafAction
    reason: Optional[str] = None
    enabled: bool = True

    class Config:
        """Pydantic config."""

        populate_by_name = True


class WafAsnUpdateRequest(BaseModel):
    """Request to update an ASN rule."""

    asn_name: Optional[str] = Field(default=None, alias="asnName")
    action: Optional[WafAction] = None
    reason: Optional[str] = None
    enabled: Optional[bool] = None

    class Config:
        """Pydantic config."""

        populate_by_name = True


class UpstreamServerCreateRequest(BaseModel):
    """Request to add an upstream server."""

    name: str
    address: str
    port: int
    protocol: ServerProtocol = ServerProtocol.HTTP
    weight: int = 1
    backup: bool = False
    health_check_path: str = Field(alias="healthCheckPath")
    region: Optional[str] = None
    country: Optional[str] = None

    class Config:
        """Pydantic config."""

        populate_by_name = True


class UpstreamServerUpdateRequest(BaseModel):
    """Request to update an upstream server."""

    name: Optional[str] = None
    address: Optional[str] = None
    port: Optional[int] = None
    protocol: Optional[ServerProtocol] = None
    weight: Optional[int] = None
    backup: Optional[bool] = None
    health_check_path: Optional[str] = Field(default=None, alias="healthCheckPath")
    region: Optional[str] = None
    country: Optional[str] = None

    class Config:
        """Pydantic config."""

        populate_by_name = True
