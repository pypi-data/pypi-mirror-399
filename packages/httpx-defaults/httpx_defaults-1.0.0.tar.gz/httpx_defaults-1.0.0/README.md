# httpx-defaults

> Production-ready httpx client with secure defaults: timeouts, retries, connection limits.

[![PyPI version](https://badge.fury.io/py/httpx-defaults.svg)](https://pypi.org/project/httpx-defaults/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## The Problem

httpx is great, but it requires you to configure timeouts, connection limits, and other production settings manually. Most developers skip this, leading to hanging requests and resource exhaustion in production.

```python
import httpx

# This can hang forever! 😱
response = httpx.get("https://slow-api.example.com")

# You need to remember all this boilerplate 😤
client = httpx.Client(
    timeout=httpx.Timeout(connect=5.0, read=30.0, write=30.0, pool=10.0),
    limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
    follow_redirects=True,
    verify=True
)
```

## The Solution

```python
from httpx_defaults import Client, AsyncClient

# Production-ready defaults out of the box! 🎉
with Client() as client:
    response = client.get("https://api.example.com")  # Safe timeouts included

# Async version
async with AsyncClient() as client:
    response = await client.get("https://api.example.com")
```

## Installation

```bash
pip install httpx-defaults
```

## Features

- **Production-ready timeouts**: 5s connect, 30s read/write, 10s pool
- **Connection limits**: 100 max connections, 20 keepalive connections  
- **Security warnings**: Alerts when using HTTP for non-localhost URLs
- **Secure by default**: HTTPS preferred, redirects followed, certificates verified
- **Drop-in replacement**: Same API as httpx.Client and httpx.AsyncClient

## Quick Start

### Basic Usage

```python
from httpx_defaults import Client, AsyncClient

# Synchronous client
with Client() as client:
    response = client.get("https://api.example.com/users")
    users = response.json()

# Asynchronous client  
async with AsyncClient() as client:
    response = await client.get("https://api.example.com/users")
    users = response.json()
```

### With Base URL and Headers

```python
from httpx_defaults import Client

with Client(
    base_url="https://api.example.com",
    headers={"Authorization": "Bearer your-token"}
) as client:
    # All requests use the base URL and headers
    response = client.get("/users")  # → https://api.example.com/users
    response = client.post("/users", json={"name": "Alice"})
```

### Convenience Functions

```python
from httpx_defaults import safe_get, safe_post

# One-shot requests with secure defaults
response = safe_get("https://api.example.com/status")
response = safe_post("https://api.example.com/webhook", json={"event": "test"})
```

## Configuration

### Custom Timeouts

```python
import httpx
from httpx_defaults import Client

# Override default timeouts
custom_timeout = httpx.Timeout(connect=2.0, read=60.0)
with Client(timeout=custom_timeout) as client:
    response = client.get("https://slow-api.example.com")
```

### Custom Connection Limits

```python
import httpx
from httpx_defaults import Client

# Override default limits
custom_limits = httpx.Limits(max_connections=50, max_keepalive_connections=10)
with Client(limits=custom_limits) as client:
    response = client.get("https://api.example.com")
```

### HTTP/2 Support

```python
from httpx_defaults import Client

# Enable HTTP/2 (requires h2 package)
with Client(http2=True) as client:
    response = client.get("https://api.example.com")
```

## Default Configuration

| Setting | Value | Reason |
|---------|-------|--------|
| Connect timeout | 5 seconds | Prevents hanging on slow DNS/connection |
| Read timeout | 30 seconds | Reasonable for most API responses |
| Write timeout | 30 seconds | Reasonable for most API requests |
| Pool timeout | 10 seconds | Prevents connection pool exhaustion |
| Max connections | 100 | Good balance for most applications |
| Keepalive connections | 20 | Efficient connection reuse |
| Follow redirects | True | Handle redirects automatically |
| Verify certificates | True | Security by default |
| HTTP/2 | False | Avoid h2 dependency by default |

## Security Features

### HTTPS Enforcement

httpx-defaults warns when you use HTTP for non-localhost URLs:

```python
from httpx_defaults import Client

with Client() as client:
    # This will show a warning ⚠️
    response = client.get("http://api.example.com")
    
    # This is fine ✅
    response = client.get("http://localhost:8000")
    response = client.get("https://api.example.com")
```

### Certificate Verification

Certificate verification is enabled by default and cannot be accidentally disabled:

```python
from httpx_defaults import Client

# Certificates are always verified ✅
with Client() as client:
    response = client.get("https://api.example.com")

# To disable verification, you must be explicit
with Client(verify=False) as client:  # Not recommended!
    response = client.get("https://self-signed.example.com")
```

## Comparison with httpx

| Feature | httpx | httpx-defaults |
|---------|-------|----------------|
| Timeouts | Manual configuration | ✅ Secure defaults |
| Connection limits | Manual configuration | ✅ Production-ready limits |
| Security warnings | None | ✅ HTTP usage warnings |
| Certificate verification | Default on | ✅ Always on by default |
| Redirect handling | Manual | ✅ Automatic |
| Dependencies | httpx only | httpx only |

## Migration from httpx

httpx-defaults is a drop-in replacement for httpx:

```python
# Before
import httpx
client = httpx.Client()

# After  
from httpx_defaults import Client
client = Client()  # Now with secure defaults!
```

All httpx.Client and httpx.AsyncClient methods work exactly the same.

## Requirements

- Python 3.10+
- httpx >= 0.25.0

## License

MIT License - Free for commercial use

## Contributing

Contributions welcome! Please see our [Contributing Guide](https://github.com/SerityOps/httpx-defaults/blob/main/CONTRIBUTING.md).

## Related Projects

- [httpx](https://github.com/encode/httpx) - The underlying HTTP client
- [asyncbridge](https://github.com/SerityOps/asyncbridge) - Async/sync conversion utilities
- [devkitx](https://github.com/SerityOps/devkitx) - Security-first Python utilities