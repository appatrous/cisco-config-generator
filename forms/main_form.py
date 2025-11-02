"""
Definition of the main input form used on the index page.

This module can leverage Flask-WTF and WTForms to declaratively
specify form fields, validation and dynamic sections.  For this
prototype a custom JavaScript-based form is used, so the classes
below are placeholders demonstrating how one might structure the
forms when migrating to WTForms.
"""

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class StaticRoute:
    destination: str
    next_hop: str
    distance: Optional[int] = None

@dataclass
class OSPFConfig:
    version: str
    process_id: Optional[int]
    router_id: Optional[str]
    networks: List[dict] = field(default_factory=list)

@dataclass
class VLAN:
    id: int
    name: Optional[str] = None

@dataclass
class AAAConfig:
    use_tacacs: bool
    tacacs_servers: List[str] = field(default_factory=list)
    use_radius: bool = False
    radius_servers: List[str] = field(default_factory=list)
    local_users: List[dict] = field(default_factory=list)

@dataclass
class MainFormData:
    platform: str
    static_routes: List[StaticRoute] = field(default_factory=list)
    ospf: Optional[OSPFConfig] = None
    vlans: List[VLAN] = field(default_factory=list)
    ntp_servers: List[str] = field(default_factory=list)
    aaa: Optional[AAAConfig] = None

    # Additional sections can be added here