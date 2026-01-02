# Thai DRG Grouper

🏥 **Thai DRG Grouper** - Multi-version Thai DRG grouper for Linux/Mac/Windows

[![PyPI version](https://badge.fury.io/py/thai-drg-grouper.svg)](https://pypi.org/project/thai-drg-grouper/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> 📖 **[เอกสารภาษาไทย (Thai Documentation)](docs/th/index.md)** | **[ตัวอย่างการใช้งาน (Examples)](docs/th/examples/basic.md)**

## ✨ Features

- ✅ **Cross-platform** - Linux, Mac, Windows
- ✅ **Multi-version** - Run multiple DRG versions simultaneously
- ✅ **Easy updates** - Add new versions with one command
- ✅ **REST API** - FastAPI included
- ✅ **CLI** - Command-line interface
- ✅ **Batch processing** - Process multiple cases at once
- ✅ **Version comparison** - Compare results across versions

## 📦 Installation

```bash
pip install thai-drg-grouper

# With API support
pip install thai-drg-grouper[api]
```

## 🚀 Quick Start

### Python Library

```python
from thai_drg_grouper import ThaiDRGGrouperManager

# Initialize with versions directory
manager = ThaiDRGGrouperManager('./data/versions')

# Group a case (uses default version)
result = manager.group_latest(
    pdx='S82201D',        # Principal diagnosis
    sdx=['E119', 'I10'],  # Secondary diagnoses
    procedures=['7936'],   # ICD-9-CM procedures
    age=25,
    sex='M',
    los=5
)

print(f"DRG: {result.drg}")      # 08172
print(f"RW: {result.rw}")        # 5.0602
print(f"AdjRW: {result.adjrw}")  # 5.0602

# Group with specific version
result = manager.group('6.3', pdx='J189', los=5)

# Compare across all versions
results = manager.group_all_versions(pdx='S82201D', los=5)
for version, res in results.items():
    print(f"{version}: DRG={res.drg}, RW={res.rw}")
```

### CLI

```bash
# List installed versions
thai-drg-grouper list

# Group a case
thai-drg-grouper group --pdx S82201D --sdx E119,I10 --proc 7936 --los 5

# Group with specific version
thai-drg-grouper group --version 6.3 --pdx J189 --los 5

# Compare across versions
thai-drg-grouper compare --pdx S82201D --los 5

# Start API server
thai-drg-grouper serve --port 8000
```

### REST API

```bash
# Start server
thai-drg-grouper serve --port 8000

# Or with uvicorn
uvicorn thai_drg_grouper.api:app --port 8000
```

**Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/versions` | List versions |
| POST | `/group` | Group (default version) |
| POST | `/group/{version}` | Group (specific version) |
| POST | `/group/compare` | Compare all versions |
| POST | `/group/batch` | Batch grouping |
| GET | `/health` | Health check |

**Example:**

```bash
curl -X POST http://localhost:8000/group \
  -H "Content-Type: application/json" \
  -d '{"pdx": "S82201D", "sdx": ["E119"], "los": 5}'
```

## 📁 Version Management

### Add Version

```bash
# From zip file
thai-drg-grouper add --version 6.4 --source /path/to/TGrp64.zip --set-default

# From folder
thai-drg-grouper add --version 6.4 --source /path/to/TGrp64/
```

### Download from TCMC

```bash
# List available versions
thai-drg-grouper download

# Download version
thai-drg-grouper download --version 6.3 --set-default
```

### Directory Structure

```
data/versions/
├── config.json           # Default settings
├── 6.3/
│   ├── version.json      # Version metadata
│   └── data/
│       ├── c63i10.dbf    # ICD-10 codes
│       ├── c63proc.dbf   # Procedures
│       ├── c63drg.dbf    # DRG definitions
│       └── c63ccex.dbf   # CC exclusions
└── 6.3.4/
    └── ...
```

## 🐳 Docker

### Using Pre-built Image from GitHub Container Registry

```bash
docker pull ghcr.io/aegisx-platform/thai-drg-grouper:latest
docker run -p 8000:8000 ghcr.io/aegisx-platform/thai-drg-grouper:latest
```

### Building Your Own Image

```dockerfile
FROM python:3.11-slim

WORKDIR /app
RUN pip install thai-drg-grouper[api]

COPY data/versions ./data/versions

EXPOSE 8000
CMD ["thai-drg-grouper", "serve", "--port", "8000"]
```

```bash
docker build -t thai-drg-grouper .
docker run -p 8000:8000 thai-drg-grouper
```

## 📊 Output Fields

| Field | Description |
|-------|-------------|
| `drg` | DRG code (5 digits) |
| `drg_name` | DRG description |
| `mdc` | Major Diagnostic Category |
| `dc` | Disease Cluster |
| `rw` | Relative Weight |
| `rw0d` | RW for day case |
| `adjrw` | Adjusted RW (by LOS) |
| `pcl` | Patient Complexity Level (0-4) |
| `is_surgical` | Surgical/Medical flag |
| `los_status` | daycase/normal/long_stay |

## 📋 Adding New Versions

When TCMC releases a new version:

```bash
# 1. Download from https://www.tcmc.or.th/tdrg
wget https://www.tcmc.or.th/.../TGrp64.zip

# 2. Add to grouper
thai-drg-grouper add --version 6.4 --source TGrp64.zip --set-default

# 3. Verify
thai-drg-grouper list
```

## ⚠️ Disclaimer

- This is an implementation based on .dbf files, **not the official grouper**
- Validate results against official TGrp before production use
- DRG data from Thai CaseMix Centre (สรท.)

## 🔗 References

- [Thai CaseMix Centre (สรท.)](https://www.tcmc.or.th)
- [Thai DRG Downloads](https://www.tcmc.or.th/tdrg)

## 💖 Support This Project

If you find this project helpful, consider buying me a coffee! ☕

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/sathit)

Your support helps maintain and improve this project!

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.
