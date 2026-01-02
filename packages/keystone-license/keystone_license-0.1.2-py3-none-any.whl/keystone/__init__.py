"""
KeyStone - License Validation Library for KeyForge

A Python library for validating software licenses against the KeyForge API.
"""

from .validator import (
    LicenseValidator,
    LicenseInfo,
    LicenseValidationError,
    validate_license
)

__version__ = "0.1.2"
__author__ = "MaskedTTN"
__all__ = [
    "LicenseValidator",
    "LicenseInfo", 
    "LicenseValidationError",
    "validate_license"
]