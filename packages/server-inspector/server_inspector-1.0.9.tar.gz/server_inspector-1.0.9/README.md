# server-inspector

Hardware detection and inventory tool.

## Purpose

Automatically detects and inventories  hardware:

- CPU information
- Memory configuration
- Storage devices (disks, NVMe, etc.)
- Network interfaces
- System capabilities

## Features

- Complete hardware inventory
- YAML output format
- Works well with [live-usb-helper](https://github.com/casaeureka/live-usb-helper)

## Usage

```bash
# Basic inspection (outputs to stdout)
sudo python3 server_inspector.py

# Save to file
sudo python3 server_inspector.py --output hardware.yml
```

## Requirements

- Must run as root for full hardware access
- Python 3.10+

## License

GPLv3 - See [LICENSE](LICENSE)

## Support

[![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsor-ea4aaa?logo=github)](https://github.com/sponsors/W3Max)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support-ff5f5f?logo=ko-fi)](https://ko-fi.com/w3max)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/w3max)
