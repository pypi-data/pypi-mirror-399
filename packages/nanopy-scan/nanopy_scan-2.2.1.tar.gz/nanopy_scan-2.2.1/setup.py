#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="nanopy-scan",
    version="2.2.1",
    author="NanoPy Team",
    author_email="dev@nanopy.chain",
    description="Full-featured blockchain explorer for NanoPy Network with SQLite indexing",
    long_description="""# NanoPy Scan

Blockchain explorer for NanoPy with SQLite indexing and WebSocket sync.

## Install

```bash
pip install nanopy-scan
nanopy-scan
```

## Networks

```bash
# NanoPy L1 Mainnet (default)
nanopy-scan --network mainnet

# NanoPy L1 Testnet
nanopy-scan --network testnet

# NanoPy Turbo L2
nanopy-scan --network turbo

# NanoPy Turbo L2 Testnet
nanopy-scan --network turbo-testnet
```

## Features

- Real-time sync via WebSocket (`eth_subscribe newHeads`)
- HTTP polling fallback
- SQLite indexing
- Block/Transaction/Address explorer
- Validator tracking
- Multi-network support (L1 + L2)

## API

| Endpoint | Description |
|----------|-------------|
| `/api/status` | Network status |
| `/api/blocks` | List blocks |
| `/api/block/:id` | Block details |
| `/api/transactions` | List transactions |
| `/api/tx/:hash` | Transaction details |
| `/api/address/:addr` | Address info |
| `/api/validators` | Validators |
""",
    long_description_content_type="text/markdown",
    url="https://github.com/nanopy/nanopy-scan",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "click>=8.0.0",
        "rich>=12.0.0",
    ],
    include_package_data=True,
    package_data={
        "nanopy_scan": ["static/*"],
    },
    entry_points={
        "console_scripts": [
            "nanopy-scan=nanopy_scan.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="blockchain explorer nanopy ethereum sqlite indexer",
)
