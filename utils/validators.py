"""
Validation helper functions.

These functions perform runtime validation of user input beyond what
HTML and Flask provide.  For example, ensuring that IP addresses
conform to IPv4/IPv6 syntax or that VLAN IDs fall within allowed
ranges.
"""

import ipaddress
import re
from typing import Union, Optional
from netaddr import IPNetwork, AddrFormatError


def is_valid_ipv4(addr: str) -> bool:
    """Check whether a string is a valid IPv4 address."""
    try:
        ipaddress.IPv4Address(addr)
        return True
    except (ipaddress.AddressValueError, ValueError):
        return False


def is_valid_ipv6(addr: str) -> bool:
    """Check whether a string is a valid IPv6 address."""
    try:
        ipaddress.IPv6Address(addr)
        return True
    except (ipaddress.AddressValueError, ValueError):
        return False


def is_valid_ip(addr: str, version: Optional[int] = None) -> bool:
    """
    Check whether a string is a valid IP address.

    Args:
        addr: IP address string to validate
        version: IP version (4 or 6). If None, accepts both.

    Returns:
        True if valid, False otherwise
    """
    if version == 4:
        return is_valid_ipv4(addr)
    elif version == 6:
        return is_valid_ipv6(addr)
    else:
        return is_valid_ipv4(addr) or is_valid_ipv6(addr)


def is_valid_subnet(subnet: str) -> bool:
    """
    Check whether a string is a valid subnet in CIDR notation.
    Supports both IPv4 and IPv6.

    Examples:
        192.168.1.0/24 -> True
        2001:db8::/32 -> True
        192.168.1.0 -> False (no prefix)
    """
    try:
        IPNetwork(subnet)
        return True
    except (AddrFormatError, ValueError):
        return False


def is_valid_vlan_id(vlan: Union[int, str]) -> bool:
    """
    Validate VLAN ID (1–4094).
    Reserved ranges: 1002-1005 (Token Ring and FDDI)
    """
    try:
        vlan_int = int(vlan)
        return 1 <= vlan_int <= 4094
    except (ValueError, TypeError):
        return False


def is_valid_interface_name(interface: str, platform: str = 'ios') -> bool:
    """
    Validate Cisco interface name format.

    Args:
        interface: Interface name (e.g., "GigabitEthernet0/0/1")
        platform: Platform type ('ios', 'nxos', 'asa')

    Returns:
        True if valid interface name format
    """
    patterns = {
        'ios': [
            r'^(FastEthernet|GigabitEthernet|TenGigabitEthernet|Ethernet)\d+(/\d+)*$',
            r'^(Loopback|Tunnel|Vlan|Port-channel)\d+$',
            r'^Serial\d+(/\d+)*$',
        ],
        'nxos': [
            r'^Ethernet\d+/\d+$',
            r'^(Loopback|Vlan|port-channel)\d+$',
            r'^mgmt\d+$',
        ],
        'asa': [
            r'^(GigabitEthernet|Management)\d+(/\d+)*$',
            r'^(inside|outside|dmz)$',
        ]
    }

    platform_patterns = patterns.get(platform, patterns['ios'])
    return any(re.match(pattern, interface, re.IGNORECASE) for pattern in platform_patterns)


def is_valid_hostname(hostname: str) -> bool:
    """
    Validate Cisco hostname.
    Rules: 1-63 characters, alphanumeric and hyphens, no leading/trailing hyphen
    """
    if not hostname or len(hostname) > 63:
        return False

    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
    return bool(re.match(pattern, hostname))


def is_valid_as_number(asn: Union[int, str]) -> bool:
    """
    Validate BGP AS number.
    Supports 2-byte (1-65535) and 4-byte (1-4294967295) AS numbers.
    """
    try:
        asn_int = int(asn)
        return 1 <= asn_int <= 4294967295
    except (ValueError, TypeError):
        return False


def is_valid_port_number(port: Union[int, str]) -> bool:
    """Validate TCP/UDP port number (1-65535)."""
    try:
        port_int = int(port)
        return 1 <= port_int <= 65535
    except (ValueError, TypeError):
        return False


def is_valid_mac_address(mac: str) -> bool:
    """
    Validate MAC address in various formats.
    Supports: aa:bb:cc:dd:ee:ff, aa-bb-cc-dd-ee-ff, aabb.ccdd.eeff
    """
    patterns = [
        r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$',  # aa:bb:cc:dd:ee:ff
        r'^([0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}$',  # aa-bb-cc-dd-ee-ff
        r'^([0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4}$', # aabb.ccdd.eeff
    ]
    return any(re.match(pattern, mac) for pattern in patterns)


def is_valid_ospf_area(area: str) -> bool:
    """
    Validate OSPF area ID.
    Can be decimal (0-4294967295) or dotted decimal (0.0.0.0 format)
    """
    # Try decimal format
    try:
        area_int = int(area)
        if 0 <= area_int <= 4294967295:
            return True
    except ValueError:
        pass

    # Try dotted decimal format
    return is_valid_ipv4(area)


def is_valid_acl_number(acl: Union[int, str]) -> bool:
    """
    Validate ACL number ranges for IOS.
    Standard: 1-99, 1300-1999
    Extended: 100-199, 2000-2699
    """
    try:
        acl_int = int(acl)
        return ((1 <= acl_int <= 99) or
                (100 <= acl_int <= 199) or
                (1300 <= acl_int <= 1999) or
                (2000 <= acl_int <= 2699))
    except (ValueError, TypeError):
        return False


def is_valid_acl_name(name: str) -> bool:
    """Validate named ACL. Alphanumeric, underscores, hyphens."""
    if not name or len(name) > 64:
        return False
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', name))


def validate_ip_with_mask(ip_mask: str) -> tuple[bool, Optional[str]]:
    """
    Validate IP address with subnet mask.

    Args:
        ip_mask: String in format "192.168.1.1 255.255.255.0" or "192.168.1.1/24"

    Returns:
        Tuple of (is_valid, error_message)
    """
    # CIDR notation
    if '/' in ip_mask:
        try:
            network = IPNetwork(ip_mask)
            return True, None
        except (AddrFormatError, ValueError) as e:
            return False, str(e)

    # Space-separated IP and mask
    parts = ip_mask.split()
    if len(parts) != 2:
        return False, "Expected format: 'IP mask' or 'IP/prefix'"

    ip_addr, mask = parts
    if not is_valid_ipv4(ip_addr):
        return False, f"Invalid IP address: {ip_addr}"
    if not is_valid_ipv4(mask):
        return False, f"Invalid subnet mask: {mask}"

    return True, None


def sanitize_input(value: str, max_length: int = 255) -> str:
    """
    Sanitize user input by removing potentially dangerous characters.
    Keeps alphanumeric, spaces, and common punctuation.
    """
    if not value:
        return ""

    # Remove control characters and limit length
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
    sanitized = sanitized[:max_length].strip()

    return sanitized