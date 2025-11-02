"""
Custom validation functions for form inputs.

This module could define reusable validators ensuring that IP
addresses, AS numbers, VLAN IDs and other parameters are valid.
Currently unused; see util/validators.py for runtime checks.
"""

def validate_ip_address(ip: str) -> bool:
    """Validate IPv4 address format (very basic)."""
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(p) < 256 for p in parts)
    except ValueError:
        return False