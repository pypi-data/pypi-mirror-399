#!/usr/bin/env python3
"""
NanoPy - Ethereum Fork Blockchain
"""

from setuptools import setup, find_packages
import os

# Read README if available
long_description = "NanoPy - Ethereum-compatible PoS blockchain in Python"
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

# Core dependencies
requirements = [
    "eth-account>=0.8.0",
    "eth-keys>=0.4.0",
    "eth-typing>=3.0.0",
    "eth-utils>=2.0.0",
    "eth-hash[pycryptodome]>=0.5.0",
    "eth-bloom>=3.0.0",
    "eth-abi>=4.0.0",
    "eth-rlp>=0.3.0",
    "rlp>=3.0.0",
    "web3>=6.0.0",
    "aiohttp>=3.8.0",
    "websockets>=10.0",
    "py-ecc>=6.0.0",
    "pycryptodome>=3.15.0",
    "ecdsa>=0.18.0",
    "trie>=2.0.0",
    "click>=8.0.0",
    "rich>=12.0.0",
    "python-dotenv>=0.20.0",
    # nanolib (P2P) dependencies - included in package, no external libp2p
    "multiaddr>=0.0.9",
    "protobuf>=3.20.0",
    "trio>=0.22.0",
    "trio-typing>=0.10.0",
    "cryptography>=3.4.0",
    "lru-dict>=1.1.0",
    "base58>=2.0.0",
    "pynacl>=1.5.0",
    "coincurve>=18.0.0",
    "trio-websocket>=0.10.0",
    "aioquic>=0.9.0",
    "noiseprotocol>=0.3.0",
    "py-multihash>=2.0.0",
    "zeroconf>=0.50.0",
    "miniupnpc>=2.2.0",
    "fastecdsa>=2.0.0; sys_platform != 'win32'",
    "grpcio>=1.50.0",
    "varint>=1.0.0",
    "psutil>=5.9.0",
]

setup(
    name="nanopy-chain",
    version="1.2.79",
    author="NanoPy Team",
    author_email="dev@nanopy.chain",
    description="A lightweight Ethereum-compatible blockchain fork with P2P networking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nanopy/nanopy-chain",
    packages=find_packages(exclude=["tests", "tests.*", "replace_imports"]),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.0",
            "black>=24.0.0",
            "mypy>=1.8.0",
            "ruff>=0.2.0",
        ],
    },
    include_package_data=True,
    package_data={
        "nanopy.genesis": ["*.json"],
    },
    entry_points={
        "console_scripts": [
            "nanopy=nanopy.cli.main:main",
            "nanopy-node=nanopy.node.main:main",
            "nanopy-validator=nanopy.validator.main:main",
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
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Distributed Computing",
    ],
    keywords="blockchain ethereum fork cryptocurrency smart-contracts",
)
