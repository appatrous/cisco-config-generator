"""
Pydantic schemas for request/response validation.
"""
from schemas.config_schemas import *
from schemas.device_schemas import *

__all__ = [
    # Config schemas
    'ConfigGenerationRequest',
    'ConfigGenerationResponse',
    'StaticRouteSchema',
    'OSPFSchema',
    'VLANSchema',

    # Device schemas
    'DeviceSchema',
    'DeviceCreateRequest',
    'DeviceUpdateRequest',
]
