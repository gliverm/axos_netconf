from typing import Optional, List
from pydantic import BaseModel, validator, constr, Field, ValidationError
from ipaddress import IPv4Address, IPv6Address


class DeviceNetconfModel(BaseModel):
    """Pydantic model for needed device parameters"""

    ipaddr: constr(max_length=15)
    username: constr(max_length=255)
    password: constr(max_length=255)
    netconfport: Optional[int] = Field(ge=1, le=65535, default=830)
    netconftimeout: Optional[int] = Field(ge=1, le=60, default=30)

    @validator("ipaddr")
    @classmethod
    def ipaddr_must_be_valid(cls, value):
        """Validate IP address"""
        try:
            IPv4Address(value)
            return value
        except ValueError:
            pass

        try:
            IPv6Address(value)
            return value
        except ValueError:
            pass

        raise ValueError("Invalid IP address")
