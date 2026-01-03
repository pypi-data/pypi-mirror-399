"""
Golden Quantum (GQ) Package Setup

Production-grade cryptographic package implementing the Golden Consensus Protocol (GCP-1)
and Golden Quantum Standard (GQS-1) for deterministic key generation.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="golden-quantum",
    version="1.0.0",
    description="Universal Golden Seed Consensus Protocol (GCP-1 & GQS-1)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="beanapologist",
    url="https://github.com/beanapologist/seed",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[],  # Zero dependencies for maximum security
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "gq-universal=gq.cli.universal:main",
            "gq-test-vectors=gq.cli.gqs1:main",
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="quantum cryptography consensus blockchain deterministic qkd gcp gqs",
    project_urls={
        "Bug Reports": "https://github.com/beanapologist/seed/issues",
        "Source": "https://github.com/beanapologist/seed",
        "Documentation": "https://github.com/beanapologist/seed#readme",
    },
)
