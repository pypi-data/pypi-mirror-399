# KeyStone-Python

KeyStone-Python is a small client library for validating KeyForge licenses
against the Keystone API (fixed endpoint: https://keystone-api.tritonstudios.co.uk).

Usage
-----
Install and import the library, then create a `LicenseValidator()` and call
`get_license_info()` or `validate()`:

```py
from keystone import LicenseValidator

v = LicenseValidator()
info = v.get_license_info("4176f215-04b5-47fe-a272-c16d4c52c864")
```

Fields returned in the parsed `LicenseInfo` object
--------------------------------------------------
- `is_active`: bool
- `tier`: string (e.g. "professional")
- `expired`: bool
- `starts_at`, `expires_at`: human-readable timestamps (strings)
- `valid`: bool
- `seats`: object { total, used, available }
- `features`: object of feature flags (bool)
- `usage`: object (limits and usage counters)
- `within_limits`: object of booleans indicating whether usage is within limits
- `metadata`: arbitrary key/value object

Example API response (representative)
-------------------------------------

```json
{
  "isActive": true,
  "tier": "professional",
  "expired": false,
  "startsAt": "2025-12-28 15:49:30",
  "expiresAt": "2026-12-28 15:49:30",
  "valid": true,
  "seats": { "total": 20, "used": 0, "available": 20 },
  "features": { "team_collaboration": true, "api_access": true },
  "usage": { "api_calls_limit": 500000, "api_calls_used": 0 },
  "within_limits": { "api_calls": true, "storage": true },
  "metadata": { "license_name": "Production License" }
}
```

Examples
--------
See the `examples/` directory for small runnable scripts demonstrating basic
validation, a detailed printer, CLI usage, decorator-based protection, and an
application-startup flow.

If you want me to update the examples directory with more sample output or
auto-run checks, tell me which examples to expand.
