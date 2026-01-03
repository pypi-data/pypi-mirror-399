"""
QuantumLock SDK - Enterprise License Validation
================================================

Protected build - core logic is compiled for security.

Version: 1.0.0
Copyright (c) 2025 SoftQuantus
"""

__version__ = "1.0.0"
__author__ = "SoftQuantus"

# Import from compiled modules
try:
    from .validator import LicenseValidator, ValidationResult
    from .client import QuantumLockClient
    from .hybrid_validator import HybridLicenseValidator
except ImportError as e:
    raise ImportError(
        "QuantumLock SDK compiled modules not found. "
        "Please ensure the package is installed correctly."
    ) from e

__all__ = [
    "LicenseValidator",
    "ValidationResult",
    "QuantumLockClient",
    "HybridLicenseValidator",
    "__version__",
]
