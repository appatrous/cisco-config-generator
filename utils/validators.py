"""
Validation helper functions.

These functions perform runtime validation of user input beyond what
HTML and Flask provide.  For example, ensuring that IP addresses
conform to IPv4/IPv6 syntax or that VLAN IDs fall within allowed
ranges.
"""

import ipaddress


def is_valid_ipv4(addr: str) -> bool:
    """Check whether a string is a valid IPv4 address."""
    try:
        ipaddress.IPv4Address(addr)
        return True
    except ipaddress.AddressValueError:
        return False


def is_valid_ipv4_network(network: str) -> bool:
    """Check whether a string is a valid IPv4 network (CIDR notation)."""
    try:
        ipaddress.IPv4Network(network, strict=False)
        return True
    except (ipaddress.AddressValueError, ValueError):
        return False


def is_valid_vlan_id(vlan: int) -> bool:
    """Validate VLAN ID (1–4094)."""
    return 1 <= vlan <= 4094
