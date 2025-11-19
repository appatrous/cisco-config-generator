"""
Pydantic schemas for configuration generation and validation.
"""
from pydantic import BaseModel, Field, validator, IPvAnyAddress
from typing import Optional, List, Dict, Any, Literal
from enum import Enum


class PlatformEnum(str, Enum):
    """Supported network device platforms."""
    IOS = "ios"
    NXOS = "nxos"
    ASA = "asa"
    EOS = "eos"
    JUNOS = "junos"


class DeviceTypeEnum(str, Enum):
    """Device type classification."""
    ROUTER = "router"
    SWITCH = "switch"
    FIREWALL = "firewall"


class ConfigFormatEnum(str, Enum):
    """Configuration output formats."""
    CLI = "cli"
    JSON = "json"
    YAML = "yaml"


# ============================================================================
# Network Protocol Schemas
# ============================================================================

class StaticRouteSchema(BaseModel):
    """Static route configuration."""
    network: str = Field(..., description="Network address (e.g., 192.168.1.0)")
    mask: str = Field(..., description="Subnet mask (e.g., 255.255.255.0)")
    next_hop: str = Field(..., description="Next hop IP address")
    description: Optional[str] = Field(None, description="Route description")
    administrative_distance: Optional[int] = Field(
        None, ge=1, le=255, description="Administrative distance (1-255)"
    )

    @validator('network', 'next_hop')
    def validate_ip_address(cls, v):
        """Validate IP address format."""
        try:
            from ipaddress import ip_address
            ip_address(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid IP address: {v}")


class OSPFSchema(BaseModel):
    """OSPF configuration."""
    process_id: int = Field(..., ge=1, le=65535, description="OSPF process ID")
    router_id: Optional[str] = Field(None, description="OSPF router ID")
    networks: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of networks to advertise"
    )
    area: int = Field(default=0, ge=0, description="OSPF area ID")
    passive_interfaces: Optional[List[str]] = Field(
        default_factory=list,
        description="List of passive interfaces"
    )
    authentication: Optional[bool] = Field(False, description="Enable authentication")


class EIGRPSchema(BaseModel):
    """EIGRP configuration."""
    as_number: int = Field(..., ge=1, le=65535, description="EIGRP AS number")
    router_id: Optional[str] = Field(None, description="EIGRP router ID")
    networks: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Networks to advertise"
    )
    passive_interfaces: Optional[List[str]] = Field(
        default_factory=list,
        description="Passive interfaces"
    )


class BGPSchema(BaseModel):
    """BGP configuration."""
    as_number: int = Field(..., ge=1, le=4294967295, description="BGP AS number")
    router_id: Optional[str] = Field(None, description="BGP router ID")
    neighbors: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="BGP neighbors"
    )
    networks: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Networks to advertise"
    )


class VLANSchema(BaseModel):
    """VLAN configuration."""
    vlan_id: int = Field(..., ge=1, le=4094, description="VLAN ID (1-4094)")
    name: str = Field(..., min_length=1, max_length=32, description="VLAN name")
    description: Optional[str] = Field(None, description="VLAN description")

    @validator('vlan_id')
    def validate_vlan_id(cls, v):
        """Validate VLAN ID is not reserved."""
        if v in [1002, 1003, 1004, 1005]:
            raise ValueError(f"VLAN {v} is reserved for legacy protocols")
        return v


class NTPSchema(BaseModel):
    """NTP server configuration."""
    servers: List[str] = Field(..., min_items=1, description="NTP server addresses")
    timezone: Optional[str] = Field("UTC", description="Timezone")
    source_interface: Optional[str] = Field(None, description="Source interface")


class AAAASchema(BaseModel):
    """AAA configuration."""
    enable_aaa: bool = Field(True, description="Enable AAA")
    authentication_method: Literal["local", "tacacs", "radius"] = Field(
        "local",
        description="Authentication method"
    )
    tacacs_servers: Optional[List[str]] = Field(
        default_factory=list,
        description="TACACS+ servers"
    )
    radius_servers: Optional[List[str]] = Field(
        default_factory=list,
        description="RADIUS servers"
    )
    shared_secret: Optional[str] = Field(None, description="Shared secret")


class ACLSchema(BaseModel):
    """Access Control List configuration."""
    acl_name: str = Field(..., description="ACL name or number")
    acl_type: Literal["standard", "extended"] = Field(
        "extended",
        description="ACL type"
    )
    entries: List[Dict[str, Any]] = Field(
        ...,
        min_items=1,
        description="ACL entries"
    )


class NATSchema(BaseModel):
    """NAT configuration."""
    nat_type: Literal["static", "dynamic", "pat"] = Field(
        ...,
        description="NAT type"
    )
    inside_interface: str = Field(..., description="Inside interface")
    outside_interface: str = Field(..., description="Outside interface")
    rules: List[Dict[str, Any]] = Field(
        ...,
        min_items=1,
        description="NAT rules"
    )


# ============================================================================
# Main Configuration Schemas
# ============================================================================

class ConfigGenerationRequest(BaseModel):
    """Request schema for configuration generation."""

    platform: PlatformEnum = Field(
        ...,
        description="Target platform (ios, nxos, asa, eos, junos)"
    )
    device_type: Optional[DeviceTypeEnum] = Field(
        None,
        description="Device type (router, switch, firewall)"
    )
    hostname: Optional[str] = Field(
        None,
        min_length=1,
        max_length=63,
        description="Device hostname"
    )

    # Basic configuration
    domain_name: Optional[str] = Field(None, description="Domain name")
    enable_secret: Optional[str] = Field(None, min_length=8, description="Enable secret")
    console_password: Optional[str] = Field(None, description="Console password")
    vty_password: Optional[str] = Field(None, description="VTY password")

    # Routing protocols
    static_routes: Optional[List[StaticRouteSchema]] = Field(
        default_factory=list,
        description="Static routes"
    )
    ospf: Optional[OSPFSchema] = Field(None, description="OSPF configuration")
    eigrp: Optional[EIGRPSchema] = Field(None, description="EIGRP configuration")
    bgp: Optional[BGPSchema] = Field(None, description="BGP configuration")

    # Layer 2
    vlans: Optional[List[VLANSchema]] = Field(
        default_factory=list,
        description="VLAN configuration"
    )

    # Services
    ntp: Optional[NTPSchema] = Field(None, description="NTP configuration")
    aaa: Optional[AAAASchema] = Field(None, description="AAA configuration")

    # Security
    acls: Optional[List[ACLSchema]] = Field(
        default_factory=list,
        description="Access control lists"
    )
    nat: Optional[NATSchema] = Field(None, description="NAT configuration")

    # Output format
    output_format: ConfigFormatEnum = Field(
        ConfigFormatEnum.CLI,
        description="Output format (cli, json, yaml)"
    )

    # Additional data
    additional_config: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional configuration data"
    )

    class Config:
        """Pydantic model configuration."""
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "platform": "ios",
                "device_type": "router",
                "hostname": "router1",
                "domain_name": "example.com",
                "static_routes": [
                    {
                        "network": "192.168.1.0",
                        "mask": "255.255.255.0",
                        "next_hop": "10.0.0.1"
                    }
                ],
                "vlans": [
                    {
                        "vlan_id": 10,
                        "name": "VLAN_10"
                    }
                ],
                "output_format": "cli"
            }
        }


class ConfigGenerationResponse(BaseModel):
    """Response schema for configuration generation."""

    success: bool = Field(..., description="Generation success status")
    platform: str = Field(..., description="Target platform")
    hostname: Optional[str] = Field(None, description="Device hostname")

    # Generated configurations
    cli_config: Optional[str] = Field(None, description="CLI format configuration")
    json_config: Optional[Dict[str, Any]] = Field(None, description="JSON format")
    yaml_config: Optional[str] = Field(None, description="YAML format")

    # Metadata
    timestamp: str = Field(..., description="Generation timestamp")
    lines_count: Optional[int] = Field(None, description="Number of config lines")

    # Validation
    validation_warnings: Optional[List[str]] = Field(
        default_factory=list,
        description="Validation warnings"
    )
    validation_errors: Optional[List[str]] = Field(
        default_factory=list,
        description="Validation errors"
    )

    # Additional info
    message: Optional[str] = Field(None, description="Additional message")
    error: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "success": True,
                "platform": "ios",
                "hostname": "router1",
                "cli_config": "hostname router1\n...",
                "timestamp": "2025-11-19T10:30:00Z",
                "lines_count": 45,
                "validation_warnings": [],
                "validation_errors": []
            }
        }


class ConfigValidationRequest(BaseModel):
    """Request schema for configuration validation."""

    platform: PlatformEnum = Field(..., description="Target platform")
    config_text: str = Field(..., min_length=1, description="Configuration text")
    validation_level: Literal["basic", "strict", "compliance"] = Field(
        "basic",
        description="Validation level"
    )

    class Config:
        """Pydantic model configuration."""
        use_enum_values = True


class ConfigValidationResponse(BaseModel):
    """Response schema for configuration validation."""

    valid: bool = Field(..., description="Overall validation status")
    platform: str = Field(..., description="Target platform")

    syntax_errors: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Syntax errors"
    )
    warnings: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Validation warnings"
    )
    compliance_issues: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Compliance issues"
    )

    summary: Dict[str, Any] = Field(..., description="Validation summary")
    timestamp: str = Field(..., description="Validation timestamp")


class ConfigComparisonRequest(BaseModel):
    """Request schema for configuration comparison."""

    config1: str = Field(..., min_length=1, description="First configuration")
    config2: str = Field(..., min_length=1, description="Second configuration")
    comparison_type: Literal["unified", "side-by-side", "context"] = Field(
        "unified",
        description="Comparison output type"
    )
    ignore_whitespace: bool = Field(True, description="Ignore whitespace differences")


class ConfigComparisonResponse(BaseModel):
    """Response schema for configuration comparison."""

    has_changes: bool = Field(..., description="Whether configurations differ")
    additions: List[str] = Field(default_factory=list, description="Added lines")
    deletions: List[str] = Field(default_factory=list, description="Deleted lines")
    modifications: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Modified lines"
    )

    statistics: Dict[str, int] = Field(..., description="Change statistics")
    diff_text: Optional[str] = Field(None, description="Full diff output")
    risk_assessment: Optional[str] = Field(None, description="Risk level assessment")
