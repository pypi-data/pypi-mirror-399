#!/usr/bin/env python3
"""
NanoLib - P2P networking library for NanoPy blockchain
Fork of py-libp2p optimized for blockchain use
"""

from setuptools import setup, find_packages

setup(
    name="nanolib-p2p",
    version="0.1.0",
    author="NanoPy Team",
    author_email="dev@nanopy.chain",
    description="P2P networking library for NanoPy blockchain (libp2p fork)",
    long_description=open("README.md").read() if __import__("os").path.exists("README.md") else "NanoLib P2P networking",
    long_description_content_type="text/markdown",
    url="https://github.com/nanopy/nanolib-p2p",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "trio>=0.22.0",
        "multiaddr>=0.0.9",
        "protobuf>=3.20.0",
        "pycryptodome>=3.15.0",
        "cryptography>=3.4.0",
        "ecdsa>=0.18.0",
        "py-ecc>=6.0.0",
        "lru-dict>=1.1.0",
        "base58>=2.0.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Networking",
        "Topic :: System :: Distributed Computing",
    ],
    keywords="p2p libp2p networking blockchain",
)
