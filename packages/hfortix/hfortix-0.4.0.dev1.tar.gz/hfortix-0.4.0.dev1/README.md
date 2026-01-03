# HFortix

Complete Python SDK for Fortinet products.

**Version:** 0.4.0-dev1 (Development)  
**Latest Stable:** 0.3.39 (PyPI)

## Overview

HFortix is a modular Python SDK for Fortinet products. Starting with v0.4.0, the package is split into focused components for flexible installation.

**By default, `hfortix` installs only the core framework.** Use extras to install specific products.

## Installation

### Complete Installation (All Products)

```bash
pip install hfortix[all]
```

This installs all Fortinet SDKs:
- `hfortix-core` - Shared foundation
- `hfortix-fortios` - FortiGate/FortiOS SDK

### Minimal Installation (Core Only)

```bash
pip install hfortix
```

This installs only `hfortix-core` (exceptions, HTTP framework).

### Product-Specific Installation

Install only what you need:

```bash
# FortiOS only
pip install hfortix[fortios]
# OR
pip install hfortix-fortios  # Includes core as dependency

# Core only (for custom implementations)
pip install hfortix-core
```

## Quick Start

```python
from hfortix import FortiOS

# Connect to FortiGate
fgt = FortiOS(
    host="192.168.1.99",
    token="your-api-token",
    verify=False
)

# Get system status
status = fgt.monitor.system.status()
print(f"Hostname: {status['hostname']}")

# Manage firewall policies
policies = fgt.firewall.policy.get()

# Use convenience wrappers (v0.3.39+)
fgt.firewall.service_custom.create(
    name="HTTPS-8443",
    tcp_portrange="8443",
    protocol="TCP/UDP/SCTP"
)
```

## Package Structure

- **hfortix** (this package) - Meta-package for convenient installation
- **hfortix-core** - Shared exceptions, HTTP client framework, utilities
- **hfortix-fortios** - FortiOS/FortiGate API client with 750+ endpoints
- **hfortix-fortimanager** - (Coming soon)
- **hfortix-fortianalyzer** - (Coming soon)

## Features

### Complete API Coverage (v0.3.39)

- **FortiOS 7.6.5**: 750+ endpoints across 77 categories
- **CMDB API**: 100% coverage (500+ endpoints)
- **Monitor API**: 100% coverage (200+ endpoints)
- **Convenience Wrappers**: Service management, schedules, traffic shaping, IP/MAC binding

### Modular Architecture (v0.4.0.dev1)

- Install only what you need
- Shared core framework for all Fortinet products
- 100% backward compatible with v0.3.x

## Documentation

See the [main repository](https://github.com/hermanwjacobsen/hfortix) for complete documentation:

- [Quick Start Guide](https://github.com/hermanwjacobsen/hfortix/blob/main/QUICKSTART.md)
- [Convenience Wrappers](https://github.com/hermanwjacobsen/hfortix/blob/main/docs/wrappers/CONVENIENCE_WRAPPERS.md)
- [Full Changelog](https://github.com/hermanwjacobsen/hfortix/blob/main/CHANGELOG.md)

## Requirements

- Python 3.10+

## License

Proprietary - See LICENSE file

