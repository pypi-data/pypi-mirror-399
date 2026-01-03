# KavachNet

[![PyPI version](https://badge.fury.io/py/kavachnet.svg)](https://badge.fury.io/py/kavachnet)
[![Python Versions](https://img.shields.io/pypi/pyversions/kavachnet.svg)](https://pypi.org/project/kavachnet/)
[![License](https://img.shields.io/pypi/l/kavachnet.svg)](https://pypi.org/project/kavachnet/)

**KavachNet** is a lightweight, real-time IP intelligence tool that instantly flags VPNs, proxies, and cloud-hosted IPs. It cross-references connections against an extensive database of **VPN IP signatures** and recognizes addresses from major providers like AWS, Azure, and Google Cloud to help secure your application against anonymized traffic. Developed and maintained by Rishabh KRW.

## Features

*   **Real-time IP Inspection**: Instantly verify if an IP (v4/v6) is a VPN, Proxy, or Tor Exit Node.
*   **Infrastructure Analyzer**: Deep scan an organization's network (using ASN or Name) to identify potential VPN hosting blocks and detect "clean" ranges.
*   **Provider Intelligence**: Search and filter fingerprints associated with specific VPN providers like NordVPN, Surfshark, and more.
*   **Advanced Detection Engine**: Supports CIDR overlap detection and multi-source cross-referencing for higher accuracy.
*   **Web Interface**: A built-in Streamlit dashboard (`kavachnet-web`) for visual analytics and infrastructure scanning.
*   **Python API**: Simple, high-performance integration for your applications with automatic dependency management.
*   **Persistent Local Intelligence**: Stores data locally in `~/.kavachnet/` using atomic writes and file-locking—fully self-contained with no external database dependencies.
*   **Auto-Update System**: Integrated engine to fetch and merge live threat intel from dozens of public and private sources.

## Installation

Install the package via pip:

```bash
pip install kavachnet
```

## Usage

### 1. Web Interface (CLI)

To launch the interactive web dashboard:

```bash
kavachnet-web
```

### 2. Python API

You can use `kavachnet` directly in your Python scripts to check IP addresses.

```python
from kavachnet import is_vpn_ip, refresh_cache

# Check a single IP
ip_to_check = "8.8.8.8"
result = is_vpn_ip(ip_to_check)

if result:
    print(f"{ip_to_check} is a VPN or Proxy IP!")
else:
    print(f"{ip_to_check} appears to be a clean or residential IP.")

# Force update the local cache of VPN IP ranges
refresh_cache()
```

## Data Updates & Storage

**KavachNet** stores its threat intelligence database locally on your machine to ensure lightning-fast lookups without constant API calls.

*   **Storage Location**: Data is stored in your home directory at `~/.kavachnet/`. The database file (`vpn_ip_list.txt`) stores a comprehensive list of subnets and IP addresses specifically identified as **VPN, Proxy, or Cloud hosting** infrastructure.
*   **Updating via Web**: Click the **"Update Database"** button in the `kavachnet-web` dashboard to fetch the latest IP ranges from all sources.
*   **Updating via API**: Programmatically update the local database using:
    ```python
    from kavachnet import refresh_cache
    refresh_cache()
    ```
*   **Updating via CLI**: You can also refresh the database directly from your terminal:
    ```bash
    python -m kavachnet.vpn_checker refresh
    ```

This approach ensures that once you update the database through the web interface, the updated data is immediately available to any Python script using the library.

## How It Works

KavachNet aggregates public IP ranges from major cloud hosting services and VPN services. When you check an IP, it verifies if the IP falls within these known subnets. The system uses a persistent local cache for high-performance detection. Built and maintained by Rishabh KRW.

## License

This project is licensed under the MIT License.
