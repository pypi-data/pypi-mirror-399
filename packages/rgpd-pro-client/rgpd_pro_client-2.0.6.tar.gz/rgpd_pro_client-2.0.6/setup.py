#!/usr/bin/env python3
"""
Setup script for RGPD_PRO CLI
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README_CLIENT.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="rgpd-pro-client",
    version="2.0.6",
    description="RGPD_PRO - Professional GDPR Compliance Scanner CLI Client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Julien",
    author_email="contact@rgpd-pro.com",  # Update with your email
    url="https://github.com/yourusername/rgpd-pro-client",  # Update with your repo
    packages=find_packages(exclude=["tests", "scan_results", "cache"]),
    
    # CLI entry point
    entry_points={
        "console_scripts": [
            "rgpd-scan=rgpd_pro_client.cli:main",
        ],
    },
    
    # Dependencies (minimal for client)
    install_requires=[
        "requests>=2.31.0",
    ],
    
    # Metadata
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Legal Industry",
        "Topic :: Security",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    
    python_requires=">=3.8",
    
    # Include data files
    include_package_data=True,
    
    keywords="gdpr compliance privacy scanner audit",
)
