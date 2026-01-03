"""DataHorders CDN SDK for Python.

A Python SDK for interacting with the DataHorders CDN API, providing
programmatic access to manage domains, zones, SSL/TLS certificates,
WAF configuration, health checks, and analytics.

Example:
    >>> from datahorders_cdn import DataHordersCDN
    >>>
    >>> # Initialize the client
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
    ...     servers=[{
    ...         "address": "10.0.1.100",
    ...         "port": 8080,
    ...         "healthCheckPath": "/health",
    ...     }],
    ... )
    >>>
    >>> # Request an ACME certificate
    >>> cert = client.certificates.create_acme(
    ...     name="example.com SSL",
    ...     domains=["example.com", "*.example.com"],
    ...     email="admin@example.com",
    ... )
"""

from datahorders_cdn.client import DataHordersCDN
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
from datahorders_cdn.models import (
    AcmeCertificateStatus,
    AcmeProvider,
    CdnNode,
    Certificate,
    CertificateProvider,
    CertificateStatus,
    Domain,
    DomainCreateResponse,
    DomainDeleteResponse,
    DomainVerifyResponse,
    HealthCheckMethod,
    HealthCheckProfile,
    HealthCheckProtocol,
    HealthCheckToggleResponse,
    HealthStatus,
    IpListType,
    LoadBalanceMethod,
    PaginationMeta,
    ServerProtocol,
    Upstream,
    UpstreamServer,
    UsageMetrics,
    WafAction,
    WafAsnRule,
    WafConfig,
    WafConfigResponse,
    WafCountryRule,
    WafIpEntry,
    WafMatchTarget,
    WafMode,
    WafRule,
    WafRuleType,
    WafSeverity,
    Zone,
    ZoneDeleteResponse,
    ZoneUsage,
)

__version__ = "1.0.0"
__author__ = "DataHorders"
__email__ = "support@datahorders.org"

__all__ = [
    # Client
    "DataHordersCDN",
    # Exceptions
    "DataHordersError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ConflictError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "DomainExistsError",
    "DomainInUseError",
    "CertificateInUseError",
    "DuplicateCertificateError",
    "InvalidCertificateError",
    "InvalidDomainsError",
    "CircularUpstreamError",
    # Enums
    "CertificateStatus",
    "CertificateProvider",
    "AcmeProvider",
    "LoadBalanceMethod",
    "ServerProtocol",
    "WafMode",
    "WafRuleType",
    "WafMatchTarget",
    "WafAction",
    "WafSeverity",
    "IpListType",
    "HealthCheckProtocol",
    "HealthCheckMethod",
    # Models
    "PaginationMeta",
    "Domain",
    "DomainCreateResponse",
    "DomainDeleteResponse",
    "DomainVerifyResponse",
    "Certificate",
    "AcmeCertificateStatus",
    "Zone",
    "ZoneDeleteResponse",
    "Upstream",
    "UpstreamServer",
    "HealthStatus",
    "HealthCheckProfile",
    "HealthCheckToggleResponse",
    "CdnNode",
    "WafConfig",
    "WafConfigResponse",
    "WafRule",
    "WafIpEntry",
    "WafCountryRule",
    "WafAsnRule",
    "UsageMetrics",
    "ZoneUsage",
]
