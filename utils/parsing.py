"""
Parsing utilities for form input.

This module could include functions to transform raw form strings
into structured data types (e.g. splitting networks into address and
prefix, converting comma-separated lists into Python lists).
"""

def parse_network(network: str):
    """Parse a network string like '192.168.1.0/24' into tuple (net, prefix).
    Returns (None, None) if invalid.
    """
    if '/' not in network:
        return None, None
    net, prefix = network.split('/', 1)
    return net, prefix