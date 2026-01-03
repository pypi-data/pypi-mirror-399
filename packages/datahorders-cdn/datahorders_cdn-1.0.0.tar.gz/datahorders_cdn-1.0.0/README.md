# DataHorders CDN Python SDK

A Python SDK for the DataHorders CDN API, providing programmatic access to manage domains, zones, SSL/TLS certificates, WAF configuration, health checks, and analytics.

## Features

- Full coverage of the DataHorders CDN API
- Both synchronous and asynchronous support
- Type hints throughout for IDE support
- Pydantic models for data validation
- Custom exceptions for error handling
- Python 3.9+ support

## Installation

```bash
pip install datahorders-cdn
```

Or install from source:

```bash
pip install git+https://github.com/datahorders/cdn-python-sdk.git
```

## Quick Start

```python
from datahorders_cdn import DataHordersCDN

# Initialize the client
client = DataHordersCDN(api_key="your-api-key")

# List all domains
domains, meta = client.domains.list()
for domain in domains:
    print(f"{domain.domain} - verified: {domain.verified}")

# Close the client when done
client.close()
```

### Using Context Manager

```python
from datahorders_cdn import DataHordersCDN

with DataHordersCDN(api_key="your-api-key") as client:
    domains, _ = client.domains.list()
    for domain in domains:
        print(domain.domain)
```

### Async Usage

```python
import asyncio
from datahorders_cdn import DataHordersCDN

async def main():
    async with DataHordersCDN(api_key="your-api-key") as client:
        domains, _ = await client.domains.list_async()
        for domain in domains:
            print(domain.domain)

asyncio.run(main())
```

## Configuration

```python
from datahorders_cdn import DataHordersCDN

client = DataHordersCDN(
    api_key="your-api-key",
    base_url="https://dashboard.datahorders.org/api/user/v1",  # Custom base URL
    timeout=60,  # Request timeout in seconds
    verify_ssl=True,  # Verify SSL certificates
)
```

## API Reference

### Domains

```python
# List domains with pagination
domains, meta = client.domains.list(page=1, per_page=20)

# Filter by verification status
verified_domains, _ = client.domains.list(verified=True)

# Get a specific domain
domain = client.domains.get(domain_id="dom_abc123")

# Register a new domain
response = client.domains.create(
    domain="example.com",
    health_check_enabled=False,
)
print(f"Verification code: {response.verification.code}")
print(response.verification.instructions)

# Verify domain ownership
result = client.domains.verify(domain="example.com")
if result.verified:
    print("Domain verified!")

# Delete a domain
client.domains.delete(domain_id="dom_abc123")
```

### Zones

```python
from datahorders_cdn import LoadBalanceMethod

# List zones
zones, meta = client.zones.list()

# Get zone by ID
zone = client.zones.get(zone_id="zone_abc123")

# Get zone by FQDN
zone = client.zones.get_by_fqdn("app.example.com")

# Create a zone
zone = client.zones.create(
    name="app",
    domains=["dom_abc123"],
    servers=[
        {
            "address": "10.0.1.100",
            "port": 8080,
            "protocol": "http",
            "healthCheckPath": "/health",
        },
        {
            "address": "10.0.1.101",
            "port": 8080,
            "protocol": "http",
            "weight": 2,
            "backup": True,
        },
    ],
    load_balance_method=LoadBalanceMethod.ROUND_ROBIN,
    upgrade_insecure=True,
    health_check_enabled=True,
)

# Update a zone
zone = client.zones.update(
    zone_id="zone_abc123",
    health_check_enabled=True,
)

# Delete a zone
client.zones.delete(fqdn="app.example.com")
```

### Certificates

```python
from datahorders_cdn import AcmeProvider

# List certificates
certs, meta = client.certificates.list()

# Get certificate by domain
cert = client.certificates.get(domain="example.com")

# Create a manual certificate
cert = client.certificates.create(
    name="example.com SSL",
    cert_content="-----BEGIN CERTIFICATE-----\n...",
    key_content="-----BEGIN PRIVATE KEY-----\n...",
)

# Request an ACME certificate
status = client.certificates.create_acme(
    name="example.com Wildcard",
    domains=["example.com", "*.example.com"],
    email="admin@example.com",
    acme_provider=AcmeProvider.LETSENCRYPT,
)
print(f"Certificate ID: {status.certificate_id}")
print(f"Status: {status.status}")

# Check ACME certificate status
status = client.certificates.get_acme_status(certificate_id="cert_abc123")
if status.status == "active":
    print("Certificate is ready!")

# Download certificate
zip_content = client.certificates.download(certificate_id="cert_abc123")
with open("certificate.zip", "wb") as f:
    f.write(zip_content)

# Delete certificate
client.certificates.delete(domain="example.com")
```

### Upstream Servers

```python
from datahorders_cdn import ServerProtocol

# List upstream servers
servers = client.upstream_servers.list(zone_id="zone_abc123")

# Add a server
server = client.upstream_servers.create(
    zone_id="zone_abc123",
    name="backend-3",
    address="10.0.1.102",
    port=8080,
    protocol=ServerProtocol.HTTP,
    weight=1,
    health_check_path="/health",
)

# Update a server
server = client.upstream_servers.update(
    zone_id="zone_abc123",
    server_id="srv_abc123",
    weight=3,
)

# Delete a server
client.upstream_servers.delete(
    zone_id="zone_abc123",
    server_id="srv_abc123",
)
```

### Health Checks

```python
from datahorders_cdn import HealthCheckProtocol, HealthCheckMethod

# List health check profiles
profiles, pagination = client.health_checks.list_profiles()

# Create a profile
profile = client.health_checks.create_profile(
    name="API Health Check",
    protocol=HealthCheckProtocol.HTTPS,
    port=443,
    path="/api/health",
    method=HealthCheckMethod.GET,
    expected_status_codes="200",
    check_interval=30,
    timeout=10,
    verify_ssl=True,
)

# Disable health checks for a server
client.health_checks.disable_server(
    server_id="srv_abc123",
    reason="Scheduled maintenance",
)

# Re-enable health checks
client.health_checks.enable_server(server_id="srv_abc123")

# List CDN nodes
nodes = client.health_checks.list_cdn_nodes()
```

### WAF (Web Application Firewall)

```python
from datahorders_cdn import (
    WafMode,
    WafRuleType,
    WafMatchTarget,
    WafAction,
    WafSeverity,
    IpListType,
)

# Get WAF configuration
waf = client.waf.get_config(zone_id="zone_abc123")
print(f"WAF enabled: {waf.config.enabled}")
print(f"Mode: {waf.config.mode}")

# Update WAF configuration
waf = client.waf.update_config(
    zone_id="zone_abc123",
    enabled=True,
    mode=WafMode.BLOCKING,
    sqli_detection=True,
    xss_detection=True,
)

# Create a WAF rule
rule = client.waf.create_rule(
    zone_id="zone_abc123",
    name="Block Admin Access",
    rule_type=WafRuleType.PATTERN,
    match_target=WafMatchTarget.URI,
    match_pattern="^/admin",
    action=WafAction.BLOCK,
    severity=WafSeverity.HIGH,
    priority=100,
)

# Block an IP address
ip_entry = client.waf.block_ip(
    zone_id="zone_abc123",
    ip_address="198.51.100.50",
    reason="Malicious activity",
)

# Allow an IP (whitelist)
ip_entry = client.waf.allow_ip(
    zone_id="zone_abc123",
    ip_address="203.0.113.0/24",
    reason="Office network",
)

# Block a country
country_rule = client.waf.add_country(
    zone_id="zone_abc123",
    country_code="XX",
    action=WafAction.BLOCK,
    reason="High risk region",
)

# Block an ASN
asn_rule = client.waf.add_asn(
    zone_id="zone_abc123",
    asn=12345,
    asn_name="Bad Hosting Provider",
    action=WafAction.BLOCK,
    reason="Known abuse source",
)
```

### Analytics

```python
from datetime import date

# Get usage metrics
usage = client.analytics.get_usage()
print(f"Total bandwidth: {usage.total_traffic.gigabytes} GB")
print(f"Total zones: {usage.total_zones}")

for zone in usage.zones:
    print(f"  {zone.zone}: {zone.gigabytes_sent} GB, {zone.requests} requests")

# Get usage for a specific date range
usage = client.analytics.get_usage(
    start_date=date(2024, 1, 1),
    end_date=date(2024, 1, 31),
)

# Get CDN node status
nodes = client.analytics.get_cdn_nodes()
for node in nodes:
    print(f"{node.domain} ({node.ip_address})")
```

## Error Handling

The SDK provides specific exception classes for different error types:

```python
from datahorders_cdn import (
    DataHordersCDN,
    DataHordersError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    DomainExistsError,
    CertificateInUseError,
)

client = DataHordersCDN(api_key="your-api-key")

try:
    domain = client.domains.create(domain="example.com")
except AuthenticationError:
    print("Invalid API key")
except DomainExistsError:
    print("Domain already registered")
except ValidationError as e:
    print(f"Validation failed: {e.message}")
    print(f"Details: {e.details}")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except NotFoundError:
    print("Resource not found")
except DataHordersError as e:
    print(f"API error: {e.message} (code: {e.code})")
```

## Exception Hierarchy

```
DataHordersError
    AuthenticationError     # 401 - Invalid credentials
    AuthorizationError      # 403 - Insufficient permissions
    NotFoundError           # 404 - Resource not found
    RateLimitError          # 429 - Rate limit exceeded
    ServerError             # 5xx - Server errors
    ConflictError           # 409 - Resource conflicts
        DomainExistsError
        DomainInUseError
        CertificateInUseError
    ValidationError         # 400 - Validation errors
        DuplicateCertificateError
        InvalidCertificateError
        InvalidDomainsError
        CircularUpstreamError
```

## Pagination

List methods return a tuple of (items, metadata):

```python
domains, meta = client.domains.list(page=1, per_page=20)

print(f"Page {meta.page} of {meta.total_pages}")
print(f"Total items: {meta.total}")

# Iterate through all pages
page = 1
while True:
    domains, meta = client.domains.list(page=page, per_page=100)
    for domain in domains:
        print(domain.domain)

    if page >= meta.total_pages:
        break
    page += 1
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/datahorders/cdn-python-sdk.git
cd cdn-python-sdk

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Type Checking

```bash
mypy datahorders_cdn
```

### Linting

```bash
ruff check datahorders_cdn
black --check datahorders_cdn
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- [Documentation](https://wiki.datahorders.org/docs/api/overview)
- [Issues](https://github.com/datahorders/cdn-python-sdk/issues)
