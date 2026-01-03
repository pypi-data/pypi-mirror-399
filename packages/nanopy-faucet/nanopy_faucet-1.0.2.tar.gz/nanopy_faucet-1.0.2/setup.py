#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="nanopy-faucet",
    version="1.0.2",
    author="NanoPy Team",
    author_email="dev@nanopy.chain",
    description="Testnet faucet for NanoPy Network",
    long_description="NanoPy Faucet - Get free testnet NPY tokens for the Pyralis testnet.",
    long_description_content_type="text/markdown",
    url="https://github.com/nanopy/nanopy-faucet",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "click>=8.0.0",
        "rich>=12.0.0",
        "eth-account>=0.8.0",
        "eth-utils>=2.0.0",
    ],
    include_package_data=True,
    package_data={
        "nanopy_faucet": ["static/*"],
    },
    entry_points={
        "console_scripts": [
            "nanopy-faucet=nanopy_faucet.main:main",
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
    keywords="blockchain faucet nanopy testnet",
)
