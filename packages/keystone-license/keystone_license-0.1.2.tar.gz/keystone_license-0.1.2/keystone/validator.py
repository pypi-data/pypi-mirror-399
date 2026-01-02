"""
KeyStone - License Validation Library

A Python library for validating software licenses against the KeyForge API.

This module is locked to use the canonical Keystone API endpoint:
https://keystone-api.tritonstudios.co.uk

Usage:
    from keystone import LicenseValidator

    validator = LicenseValidator()  # uses the fixed Keystone API endpoint

    if validator.validate("your-license-key"):
        print("License is valid!")
    else:
        print("Invalid license")
"""

import requests
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class LicenseInfo:
    """Represents license information returned from the API"""
    is_active: bool
    tier: str
    expired: bool
    starts_at: str
    expires_at: str
    valid: bool
    seats: dict
    features: dict
    usage: dict
    within_limits: dict
    metadata: dict
    
    @property
    def days_until_expiry(self) -> int:
        """Calculate days until license expires"""
        try:
            expires = datetime.strptime(self.expires_at, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            delta = expires - now
            return max(0, delta.days)
        except Exception:
            return 0
    
    @property
    def is_expired(self) -> bool:
        """Check if license is expired"""
        return self.expired
    
    @property
    def is_valid(self) -> bool:
        """Check if license is valid (active and not expired)"""
        return self.valid


class LicenseValidationError(Exception):
    """Raised when license validation fails"""
    pass


DEFAULT_API_URL = "https://keystone-api.tritonstudios.co.uk"


class LicenseValidator:
    """
    Validates software licenses against the SaaSKey API
    
    Example:
        validator = LicenseValidator()
        
        # Simple validation
        if validator.validate("abc-123-def"):
            print("Valid!")
        
        # Get detailed info
        license_info = validator.get_license_info("abc-123-def")
        print(f"Tier: {license_info.tier}")
        print(f"Days left: {license_info.days_until_expiry}")
    """
    
    def __init__(self, timeout: int = 10, cache_duration: int = 300):
        """
        Initialize the license validator.

        Uses the fixed Keystone API endpoint defined by `DEFAULT_API_URL`.

        Args:
            timeout: Request timeout in seconds (default: 10)
            cache_duration: How long to cache validation results in seconds (default: 300)
        """
        self.api_url = DEFAULT_API_URL
        self.timeout = timeout
        self.cache_duration = cache_duration
        self._cache: Dict[str, tuple[LicenseInfo, datetime]] = {}
    
    def validate(self, license_key: str, use_cache: bool = True) -> bool:
        """
        Validate a license key
        
        Args:
            license_key: The license key to validate
            use_cache: Whether to use cached results (default: True)
        
        Returns:
            True if license is valid, False otherwise
        
        Example:
            if validator.validate("my-license-key"):
                print("License is valid!")
        """
        try:
            info = self.get_license_info(license_key, use_cache=use_cache)
            return info.is_valid if info else False
        except LicenseValidationError:
            return False
    
    def get_license_info(self, license_key: str, use_cache: bool = True) -> Optional[LicenseInfo]:
        """
        Get detailed license information
        
        Args:
            license_key: The license key to query
            use_cache: Whether to use cached results (default: True)
        
        Returns:
            LicenseInfo object or None if license not found
        
        Raises:
            LicenseValidationError: If API request fails
        
        Example:
            info = validator.get_license_info("my-key")
            if info and info.is_valid:
                print(f"License tier: {info.tier}")
                print(f"Expires in {info.days_until_expiry} days")
        """
        # Check cache first
        if use_cache and license_key in self._cache:
            cached_info, cached_time = self._cache[license_key]
            age = (datetime.now() - cached_time).total_seconds()
            if age < self.cache_duration:
                return cached_info
        
        # Make API request
        url = f"{self.api_url}/license/{license_key}"
        
        try:
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 404:
                return None
            
            if response.status_code != 200:
                raise LicenseValidationError(
                    f"API returned status code {response.status_code}"
                )
            
            data = response.json()
            # API may return { "license": { ... } } or the license object directly
            lic = data.get('license') if isinstance(data, dict) and 'license' in data else data

            # Map fields from the new KeyForge shape
            is_active = lic.get('isActive', lic.get('is_active', False))
            tier = lic.get('tier', '')

            # Compute starts_at / expires_at from created_at + duration (hours)
            created = lic.get('created_at') or lic.get('date') or lic.get('startsAt')
            duration = lic.get('duration')
            starts_at = created if created else ''
            expires_at = ''
            expired = False

            if created and duration:
                try:
                    if isinstance(created, str):
                        created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    else:
                        created_dt = created

                    expires_dt = created_dt + timedelta(hours=int(duration))
                    starts_at = created_dt.strftime("%Y-%m-%d %H:%M:%S")
                    expires_at = expires_dt.strftime("%Y-%m-%d %H:%M:%S")
                    expired = datetime.now(tz=created_dt.tzinfo) > expires_dt
                except Exception:
                    # Fall back to raw strings if parsing fails
                    expires_at = str(created)

            valid = bool(is_active) and not expired

            seats = lic.get('seats', {})
            features = lic.get('features', {})
            usage = lic.get('usage', {})
            within_limits = lic.get('within_limits', lic.get('withinLimits', {}))
            metadata = lic.get('metadata', {})

            license_info = LicenseInfo(
                is_active=bool(is_active),
                tier=tier,
                expired=bool(expired),
                starts_at=starts_at,
                expires_at=expires_at,
                valid=bool(valid),
                seats=seats,
                features=features,
                usage=usage,
                within_limits=within_limits,
                metadata=metadata,
            )
            
            # Cache the result
            self._cache[license_key] = (license_info, datetime.now())
            
            return license_info
            
        except requests.exceptions.Timeout:
            raise LicenseValidationError("API request timed out")
        except requests.exceptions.ConnectionError:
            raise LicenseValidationError("Failed to connect to API")
        except requests.exceptions.RequestException as e:
            raise LicenseValidationError(f"API request failed: {str(e)}")
        except (KeyError, ValueError) as e:
            raise LicenseValidationError(f"Invalid API response: {str(e)}")
    
    def require_license(self, license_key: str, min_tier: Optional[str] = None) -> LicenseInfo:
        """
        Validate license and raise exception if invalid
        
        Args:
            license_key: The license key to validate
            min_tier: Optional minimum tier required (e.g., "pro" or "premium")
        
        Returns:
            LicenseInfo object if valid
        
        Raises:
            LicenseValidationError: If license is invalid or tier insufficient
        
        Example:
            try:
                info = validator.require_license("my-key", min_tier="pro")
                print("License verified!")
            except LicenseValidationError as e:
                print(f"License error: {e}")
                sys.exit(1)
        """
        info = self.get_license_info(license_key)
        
        if not info:
            raise LicenseValidationError("License key not found")
        
        if not info.is_valid:
            if info.is_expired:
                raise LicenseValidationError("License has expired")
            else:
                raise LicenseValidationError("License is not active")
        
        # Check tier if specified
        if min_tier:
            tier_hierarchy = {"basic": 1, "pro": 2, "premium": 3}
            required_level = tier_hierarchy.get(min_tier.lower(), 0)
            current_level = tier_hierarchy.get(info.tier.lower(), 0)
            
            if current_level < required_level:
                raise LicenseValidationError(
                    f"License tier '{info.tier}' insufficient. Required: '{min_tier}' or higher"
                )
        
        return info
    
    def clear_cache(self):
        """Clear the license validation cache"""
        self._cache.clear()
    
    def check_tier(self, license_key: str, required_tier: str) -> bool:
        """
        Check if license has a specific tier or higher
        
        Args:
            license_key: The license key to check
            required_tier: Required tier ("basic", "pro", or "premium")
        
        Returns:
            True if license tier is sufficient
        
        Example:
            if validator.check_tier("my-key", "pro"):
                print("Pro features unlocked!")
        """
        try:
            self.require_license(license_key, min_tier=required_tier)
            return True
        except LicenseValidationError:
            return False


# Convenience function for simple validation
def validate_license(license_key: str) -> bool:
    """
    Quick validation function without creating a validator instance.

    This always uses the fixed Keystone API endpoint.

    Args:
        license_key: The license key to validate

    Returns:
        True if valid, False otherwise

    Example:
        if validate_license("my-key"):
            print("Valid!")
    """
    validator = LicenseValidator()
    return validator.validate(license_key)


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python saaskey.py <LICENSE_KEY>")
        sys.exit(1)

    license_key = sys.argv[1]

    validator = LicenseValidator()
    
    try:
        info = validator.get_license_info(license_key)
        
        if not info:
            print(f"❌ License key '{license_key}' not found")
            sys.exit(1)
        
        if info.is_valid:
            print(f"✅ License is valid!")
            print(f"   Tier: {info.tier}")
            print(f"   Active: {info.is_active}")
            print(f"   Expires: {info.expires_at}")
            print(f"   Days remaining: {info.days_until_expiry}")
        else:
            print(f"❌ License is invalid")
            if info.is_expired:
                print(f"   Reason: Expired on {info.expires_at}")
            else:
                print(f"   Reason: Not active")
            sys.exit(1)
            
    except LicenseValidationError as e:
        print(f"❌ Validation error: {e}")
        sys.exit(1)