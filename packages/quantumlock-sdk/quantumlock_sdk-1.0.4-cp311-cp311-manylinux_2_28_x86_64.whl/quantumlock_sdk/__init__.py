"""
QuantumLock SDK - Enterprise License Validation
================================================

Protected build - core logic is compiled for security.

Version: 1.0.4
Copyright (c) 2026 SoftQuantus
"""

__version__ = "1.0.4"
__author__ = "SoftQuantus"

# Import from compiled modules
try:
    from .validator import LicenseValidator, LicenseError, FeatureNotLicensed
    from .validator_v2 import LicenseValidatorV2, ValidationResult, ValidationError
    from .client import QuantumLockClient
    from .hybrid_validator import HybridLicenseValidator
except ImportError as e:
    raise ImportError(
        "QuantumLock SDK compiled modules not found. "
        "Please ensure the package is installed correctly."
    ) from e

__all__ = [
    "LicenseValidator",
    "LicenseValidatorV2",
    "LicenseError",
    "FeatureNotLicensed",
    "ValidationResult",
    "ValidationError",
    "QuantumLockClient",
    "HybridLicenseValidator",
    "__version__",
]
