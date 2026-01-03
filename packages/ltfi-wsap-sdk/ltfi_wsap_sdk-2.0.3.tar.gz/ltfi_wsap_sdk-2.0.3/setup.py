"""
WSAP Python SDK
Setup configuration for PyPI distribution
"""

from setuptools import setup, find_packages

# Read the full README for GitHub
with open("README.md", "r", encoding="utf-8") as fh:
    github_description = fh.read()

# PyPI-friendly description without external images
pypi_description = """# LTFI-WSAP Python SDK

[![PyPI version](https://badge.fury.io/py/ltfi-wsap-sdk.svg)](https://pypi.org/project/ltfi-wsap-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/KiefStudioMA/ltfi-wsap-python/blob/main/LICENSE)
[![LTFI-WSAP](https://img.shields.io/badge/LTFI--WSAP-v2.0.0-blue.svg)](https://wsap.ltfi.ai)
[![Kief Studio](https://img.shields.io/badge/By-Kief%20Studio-green.svg)](https://kief.studio)

Official Python SDK for **LTFI-WSAP** (Layered Transformer Framework Intelligence - Web System Alignment Protocol) by **Kief Studio**.

Part of the [LTFI Ecosystem](https://ltfi.ai) • [WSAP Protocol](https://wsap.ltfi.ai)

## 📦 Installation

```bash
pip install ltfi-wsap-sdk
```

For development or to get the latest changes:
```bash
pip install git+https://github.com/KiefStudioMA/ltfi-wsap-python.git
```

## 🚀 Quick Start

```python
from ltfi_wsap import WSAPClient

# Initialize the client
client = WSAPClient(api_key="your-api-key")

# Get entity information
entity = client.entities.get("entity-id")
print(f"Entity: {entity.name}")

# Verify a domain
verification = client.verify_domain("example.com")
print(f"Domain verified: {verification.verified}")

# Generate WSAP JSON
wsap_json = client.generate_wsap("entity-id")
print(wsap_json)
```

## 📚 Documentation

- **Main Documentation**: [docs.ltfi.ai](https://docs.ltfi.ai)
- **API Reference**: [api.ltfi.ai/docs](https://api.ltfi.ai/docs)
- **Examples**: [github.com/KiefStudioMA/LTFI-WSAP-Examples](https://github.com/KiefStudioMA/LTFI-WSAP-Examples)

## 🔑 Features

- ✅ Full WSAP protocol implementation
- ✅ Entity management (CRUD operations)
- ✅ Domain verification (DNS TXT, file upload, meta tags)
- ✅ Progressive disclosure levels (BASIC, STANDARD, DETAILED, COMPLETE)
- ✅ Field-level encryption for sensitive data
- ✅ Async/await support
- ✅ Type hints for better IDE support
- ✅ Comprehensive error handling
- ✅ Retry logic with exponential backoff
- ✅ Rate limiting support

## 📄 License

**MIT License** - This SDK is open source and free to use.

See [LICENSE](https://github.com/KiefStudioMA/ltfi-wsap-python/blob/main/LICENSE) for full terms.

### LTFI-WSAP Service Usage

While this SDK is open source, the LTFI-WSAP service has the following usage terms:

- ✅ **FREE** for personal use, open source projects, and small businesses
- ✅ **FREE** for most users and use cases
- 💳 **Paid plans** required for:
  - Enterprises with annual revenue exceeding $1M USD
  - Organizations managing more than 100 domains
  - High-volume API usage

For pricing details: [wsap.ltfi.ai/pricing](https://wsap.ltfi.ai/pricing)

## 🆘 Support

- **Technical Support**: developers@kief.studio
- **Business Inquiries**: business@kief.studio
- **Discord**: [discord.gg/JfjyUdjJgP](https://discord.gg/JfjyUdjJgP)
- **X (Twitter)**: [x.com/kief_ma](https://x.com/kief_ma)
- **LinkedIn**: [linkedin.com/company/kief-studio](https://www.linkedin.com/company/kief-studio/)

---

**Built with ❤️ by [Kief Studio](https://kief.studio)**

Part of the [LTFI Ecosystem](https://ltfi.ai) • [WSAP Protocol](https://wsap.ltfi.ai)

© 2025 Kief Studio, MA. All rights reserved.

**Open Source SDK - Service usage subject to terms**
"""

setup(
    name="ltfi-wsap-sdk",
    version="2.0.3",  # Fixed PyPI display
    author="Kief Studio",
    author_email="developers@kief.studio",
    maintainer="LTFI Team",
    maintainer_email="support@wsap.ltfi.ai",
    description="Official Python SDK for LTFI-WSAP (Web System Alignment Protocol) by Kief Studio - Part of the LTFI ecosystem",
    long_description=pypi_description,  # Use PyPI-friendly version
    long_description_content_type="text/markdown",
    url="https://github.com/KiefStudioMA/LTFI-WSAP-Python",
    packages=find_packages(exclude=["tests", "examples"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.28.0",
        "pydantic>=2.0.0",
        "cryptography>=41.0.0",
        "dnspython>=2.3.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "async": ["aiohttp>=3.8.0", "asyncio>=3.4.3"],
        "cli": ["click>=8.0.0", "rich>=13.0.0", "tabulate>=0.9.0"],
        "django": ["django>=3.2"],
        "flask": ["flask>=2.0.0"],
        "cache": ["redis>=4.5.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ltfi-wsap=ltfi_wsap.cli:main",
        ],
    },
    project_urls={
        "Documentation": "https://docs.ltfi.ai",
        "Bug Reports": "https://github.com/KiefStudioMA/LTFI-WSAP-Python/issues",
        "Source": "https://github.com/KiefStudioMA/LTFI-WSAP-Python",
        "Discord": "https://discord.gg/JfjyUdjJgP",
        "Company": "https://kief.studio",
        "LTFI Ecosystem": "https://ltfi.ai",
        "WSAP Protocol": "https://wsap.ltfi.ai",
    },
    keywords="wsap verification domain security api sdk kief-studio ltfi ai-verification organizational-data",
    license="MIT",
    include_package_data=True,
    zip_safe=False,
)