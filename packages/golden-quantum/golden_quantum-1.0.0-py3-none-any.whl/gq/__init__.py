"""
Golden Quantum (GQ) - Universal Cryptographic Key Generation

This package provides production-grade implementations of:
- GCP-1: Golden Consensus Protocol v1.0 (Universal QKD Key Generator)
- GQS-1: Golden Quantum Standard (Test Vector Generation)

Both protocols use the golden seed (iφ) as a root of trust for deterministic,
cryptographically strong key generation with forward secrecy.

Example Usage:
    >>> from gq import UniversalQKD, GQS1
    >>>
    >>> # Generate keys using GCP-1 (Universal QKD)
    >>> generator = UniversalQKD()
    >>> key = next(generator)
    >>> print(key.hex())
    '3c732e0d04dac163a5cc2b15c7caf42c'
    >>>
    >>> # Generate test vectors using GQS-1
    >>> vectors = GQS1.generate_test_vectors(10)
    >>> print(vectors[0])
    'a01611f01e8207a27c1529c3650c4838'
"""

from .universal_qkd import (
    universal_qkd_generator as UniversalQKD,
    generate_keys as generate_universal_keys,
    HEX_SEED,
    EXPECTED_CHECKSUM,
)

from .gqs1 import (
    generate_test_vectors as generate_gqs1_vectors,
    GQS1,
)

__all__ = [
    "UniversalQKD",
    "generate_universal_keys",
    "GQS1",
    "generate_gqs1_vectors",
    "HEX_SEED",
    "EXPECTED_CHECKSUM",
]

__version__ = "1.0.0"
__protocol_gcp__ = "GCP-1"
__protocol_gqs__ = "GQS-1"
__author__ = "beanapologist"
