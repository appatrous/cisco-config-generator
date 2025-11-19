"""
Pydantic schemas for device management.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from schemas.config_schemas import PlatformEnum, DeviceTypeEnum


class DeviceSchema(BaseModel):
    """Complete device schema with all fields."""

    id: int = Field(..., description="Device ID")
    hostname: str = Field(..., min_length=1, max_length=255, description="Device hostname")
    ip_address: str = Field(..., description="Device IP address")
    platform: PlatformEnum = Field(..., description="Device platform")
    device_type: DeviceTypeEnum = Field(..., description="Device type")

    # Optional fields
    location: Optional[str] = Field(None, max_length=255, description="Physical location")
    model: Optional[str] = Field(None, max_length=100, description="Device model")
    os_version: Optional[str] = Field(None, max_length=100, description="OS version")
    serial_number: Optional[str] = Field(None, max_length=100, description="Serial number")

    # Status fields
    status: Optional[str] = Field("unknown", description="Device status")
    last_seen: Optional[datetime] = Field(None, description="Last seen timestamp")

    # Credentials (ID only for security)
    credential_id: Optional[int] = Field(None, description="Credential ID")

    # Organization
    organization_id: int = Field(..., description="Organization ID")

    # Metadata
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")

    class Config:
        """Pydantic model configuration."""
        from_attributes = True
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "hostname": "router1",
                "ip_address": "192.168.1.1",
                "platform": "ios",
                "device_type": "router",
                "location": "Data Center 1",
                "status": "reachable",
                "organization_id": 1,
                "created_at": "2025-11-19T10:00:00Z",
                "updated_at": "2025-11-19T10:00:00Z"
            }
        }


class DeviceCreateRequest(BaseModel):
    """Request schema for creating a new device."""

    hostname: str = Field(..., min_length=1, max_length=255, description="Device hostname")
    ip_address: str = Field(..., description="Device IP address")
    platform: PlatformEnum = Field(..., description="Device platform")
    device_type: DeviceTypeEnum = Field(..., description="Device type")

    # Optional fields
    location: Optional[str] = Field(None, max_length=255, description="Physical location")
    model: Optional[str] = Field(None, max_length=100, description="Device model")
    os_version: Optional[str] = Field(None, max_length=100, description="OS version")
    serial_number: Optional[str] = Field(None, max_length=100, description="Serial number")

    # Credentials
    username: Optional[str] = Field(None, description="Device username")
    password: Optional[str] = Field(None, description="Device password")
    enable_password: Optional[str] = Field(None, description="Enable password")

    @validator('ip_address')
    def validate_ip_address(cls, v):
        """Validate IP address format."""
        try:
            from ipaddress import ip_address
            ip_address(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid IP address: {v}")

    @validator('hostname')
    def validate_hostname(cls, v):
        """Validate hostname format."""
        import re
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]$', v):
            raise ValueError(
                "Hostname must start and end with alphanumeric characters "
                "and can only contain alphanumerics and hyphens"
            )
        return v

    class Config:
        """Pydantic model configuration."""
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "hostname": "router1",
                "ip_address": "192.168.1.1",
                "platform": "ios",
                "device_type": "router",
                "location": "Data Center 1",
                "username": "admin",
                "password": "secure_password"
            }
        }


class DeviceUpdateRequest(BaseModel):
    """Request schema for updating a device."""

    hostname: Optional[str] = Field(None, min_length=1, max_length=255)
    ip_address: Optional[str] = Field(None)
    platform: Optional[PlatformEnum] = Field(None)
    device_type: Optional[DeviceTypeEnum] = Field(None)
    location: Optional[str] = Field(None, max_length=255)
    model: Optional[str] = Field(None, max_length=100)
    os_version: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None)

    # Credentials
    username: Optional[str] = Field(None)
    password: Optional[str] = Field(None)
    enable_password: Optional[str] = Field(None)

    @validator('ip_address')
    def validate_ip_address(cls, v):
        """Validate IP address format."""
        if v is not None:
            try:
                from ipaddress import ip_address
                ip_address(v)
            except ValueError:
                raise ValueError(f"Invalid IP address: {v}")
        return v

    class Config:
        """Pydantic model configuration."""
        use_enum_values = True


class DeviceBulkImportRequest(BaseModel):
    """Request schema for bulk device import."""

    devices: List[DeviceCreateRequest] = Field(
        ...,
        min_items=1,
        description="List of devices to import"
    )
    skip_duplicates: bool = Field(
        False,
        description="Skip devices with duplicate hostnames/IPs"
    )
    validate_connectivity: bool = Field(
        False,
        description="Validate connectivity before import"
    )


class DevicePingRequest(BaseModel):
    """Request schema for device ping/connectivity test."""

    timeout: int = Field(5, ge=1, le=30, description="Timeout in seconds")
    count: int = Field(4, ge=1, le=10, description="Number of ping attempts")


class DevicePingResponse(BaseModel):
    """Response schema for device ping/connectivity test."""

    success: bool = Field(..., description="Ping success status")
    reachable: bool = Field(..., description="Device reachability")
    device_id: int = Field(..., description="Device ID")
    hostname: str = Field(..., description="Device hostname")
    ip_address: str = Field(..., description="Device IP address")

    # Ping statistics
    packets_sent: int = Field(..., description="Packets sent")
    packets_received: int = Field(..., description="Packets received")
    packet_loss_percent: float = Field(..., description="Packet loss percentage")

    # Timing
    min_rtt: Optional[float] = Field(None, description="Minimum RTT (ms)")
    avg_rtt: Optional[float] = Field(None, description="Average RTT (ms)")
    max_rtt: Optional[float] = Field(None, description="Maximum RTT (ms)")

    # Error message if failed
    error: Optional[str] = Field(None, description="Error message")
    timestamp: datetime = Field(..., description="Test timestamp")


class DeviceHealthCheckResponse(BaseModel):
    """Response schema for device health check."""

    device_id: int = Field(..., description="Device ID")
    hostname: str = Field(..., description="Device hostname")
    status: Literal["healthy", "degraded", "unreachable", "unknown"] = Field(
        ...,
        description="Health status"
    )

    # Health metrics
    reachable: bool = Field(..., description="Device reachability")
    cpu_usage: Optional[float] = Field(None, ge=0, le=100, description="CPU usage %")
    memory_usage: Optional[float] = Field(None, ge=0, le=100, description="Memory usage %")
    uptime: Optional[int] = Field(None, description="Uptime in seconds")

    # Interface statistics
    interfaces_up: Optional[int] = Field(None, description="Number of interfaces up")
    interfaces_down: Optional[int] = Field(None, description="Number of interfaces down")

    # Checks performed
    checks: Dict[str, bool] = Field(..., description="Individual check results")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    errors: List[str] = Field(default_factory=list, description="Error messages")

    # Timestamp
    timestamp: datetime = Field(..., description="Health check timestamp")


class DeviceStatisticsResponse(BaseModel):
    """Response schema for device statistics."""

    total_devices: int = Field(..., description="Total number of devices")
    devices_by_platform: Dict[str, int] = Field(
        ...,
        description="Devices grouped by platform"
    )
    devices_by_type: Dict[str, int] = Field(
        ...,
        description="Devices grouped by type"
    )
    devices_by_status: Dict[str, int] = Field(
        ...,
        description="Devices grouped by status"
    )

    # Health summary
    reachable: int = Field(..., description="Number of reachable devices")
    unreachable: int = Field(..., description="Number of unreachable devices")
    unknown: int = Field(..., description="Number of devices with unknown status")

    # Recent activity
    recently_added: int = Field(..., description="Devices added in last 7 days")
    recently_updated: int = Field(..., description="Devices updated in last 7 days")

    # Timestamp
    timestamp: datetime = Field(..., description="Statistics generation timestamp")
