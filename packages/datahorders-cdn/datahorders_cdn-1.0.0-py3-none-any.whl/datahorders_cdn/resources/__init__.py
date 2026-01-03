"""Resource modules for the DataHorders CDN SDK."""

from datahorders_cdn.resources.analytics import AnalyticsResource
from datahorders_cdn.resources.certificates import CertificatesResource
from datahorders_cdn.resources.domains import DomainsResource
from datahorders_cdn.resources.health_checks import HealthChecksResource
from datahorders_cdn.resources.upstream_servers import UpstreamServersResource
from datahorders_cdn.resources.waf import WafResource
from datahorders_cdn.resources.zones import ZonesResource

__all__ = [
    "AnalyticsResource",
    "CertificatesResource",
    "DomainsResource",
    "HealthChecksResource",
    "UpstreamServersResource",
    "WafResource",
    "ZonesResource",
]
