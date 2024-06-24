"""
Device file config class

Design Notes:
*   Device file is a YAML file containing device configuration information.
*   Devices validated using pydantic.
*   All models allow for extra fields validating only the fields defined.
*   All models are case insensitive keys.
*   Validiation is not implace to assume knowledge of device types to
    valid connection types

Initial preferred method of use from CLI scripts:

from app.lib.cli_utils.devicecfg import Devices, DeviceCfgError

DEVICES_FILE = "config/devices.yaml"
# Load devices from file into Devices object
devices = Devices(DEVICES_FILE)
# Get device connection parameters
device_conn_params = devices.get_device_connection_params("simob", "netconf")


Example device file:
devices:
    simob:
        type: 'axos'
        connections:
            netconf:
                type: 'netconf'
                host: "10.137.12.159"
                username: "calixsupport"
                password: "calixsupport"
                port: 830
                timeout: 60
            ssh:
                type: 'ssh'
                host: "10.137.12.159"
                username: "calixsupport"
                password: "calixsupport"
                port: 22
                timeout: 60
    smx:
        type: 'smx'
        connections:
            rest:
                type: 'rest'
                host: sjcx-smx04.calix.local
                username: admin
                password: test123
                apiport: 18443
                apiroot: "/rest/v1"
"""

import time
from enum import Enum
from typing import Optional, Dict, Union, Literal, List, IO
from ipaddress import IPv4Address, IPv6Address
from fqdn import FQDN
import yaml
from pydantic import BaseModel, constr, Field, field_validator, ConfigDict

from lib.cli_utils.errors import DeviceCfgError


class ConnectionTypeEnum(str, Enum):
    """Connection type enum"""

    NETCONF = "netconf"
    SSH = "ssh"
    REST = "rest"
    FTP = "ftp"


class DeviceTypeEnum(str, Enum):
    """Device type enum"""

    AXOS = "axos"
    SMX = "smx"
    FTP = "ftp"


def _validate_host(value: str) -> str:
    """Validate host is either an fdqn, IPv4 address, or IPv6 address"""
    try:
        IPv4Address(value)
        return value
    except ValueError:
        pass

    try:
        if not FQDN(value).is_valid:
            raise ValueError("Invalid FQDN")
        return value
    except ValueError:
        pass

    try:
        IPv6Address(value)
        return value
    except ValueError:
        pass

    raise ValueError("Invalid IPv4, FQDN, IPv6")


class SmxRestConnectionModel(BaseModel):
    """SMX Rest API device connection parameters"""

    model_config = ConfigDict(extra="ignore")
    type: Literal["rest"]
    host: str
    username: constr(max_length=255)
    password: constr(max_length=255)
    apiport: Optional[int] = 18443
    apiroot: Optional[str] = "/rest/v1"

    # class Config:
    #     """Pydantic model configuration"""

    #     extra = "ignore"

    @field_validator("host")
    @classmethod
    def host_must_be_valid(cls, value: str) -> str:
        """Validate host"""
        return _validate_host(value)


class NetconfConnectionModel(BaseModel):
    """Netconf device connection parameters"""

    model_config = ConfigDict(extra="ignore")
    type: Literal["netconf"]
    host: str
    username: constr(max_length=255)
    password: constr(max_length=255)
    port: Optional[int] = Field(ge=1, le=65535, default=830)
    timeout: Optional[int] = Field(ge=1, le=120, default=60)

    # class Config:
    #     """Pydantic model configuration"""

    #     extra = "ignore"

    @field_validator("host")
    @classmethod
    def host_must_be_valid(cls, value: str) -> str:
        """Validate host"""
        return _validate_host(value)


class SshConnectionModel(BaseModel):
    """SSH device connection parameters"""

    model_config = ConfigDict(extra="ignore")
    type: Literal["ssh"]
    host: str
    username: constr(max_length=255)
    password: constr(max_length=255)
    port: Optional[int] = Field(ge=1, le=65535, default=22)
    timeout: Optional[int] = Field(ge=1, le=120, default=60)

    # class Config:
    #     """Pydantic model configuration"""

    #     extra = "ignore"

    @field_validator("host")
    @classmethod
    def host_must_be_valid(cls, value: str) -> str:
        """Validate host"""
        return _validate_host(value)


class FtpConnectionModel(BaseModel):
    """FTP device connection parameters"""

    model_config = ConfigDict(extra="ignore")
    type: Literal["ftp"]
    host: str
    username: constr(max_length=255)
    password: constr(max_length=255)
    port: Optional[int] = Field(ge=1, le=65535, default=21)
    timeout: Optional[int] = Field(ge=1, le=120, default=60)

    # class Config:
    #     """Pydantic model configuration"""

    #     extra = "ignore"

    @field_validator("host")
    @classmethod
    def host_must_be_valid(cls, value: str) -> str:
        """Validate host"""
        return _validate_host(value)


class DeviceModel(BaseModel):
    """Single device model"""

    model_config = ConfigDict(extra="ignore")
    type: DeviceTypeEnum
    connections: Dict[
        str,
        Union[
            NetconfConnectionModel,
            SshConnectionModel,
            SmxRestConnectionModel,
            FtpConnectionModel,
        ],
    ]

    # class Config:
    #     """Pydantic model configuration"""

    #     extra = "ignore"


class DevicesModel(BaseModel):
    """Multiple devices model"""

    model_config = ConfigDict(extra="ignore")
    devices: Dict[str, DeviceModel]

    # class Config:
    #     """Pydantic model configuration"""

    #     extra = "ignore"


class Device:
    """Common device class for all devices"""

    def __init__(self, device_model: DeviceModel):
        self.__device = device_model

    @property
    def device(self) -> DeviceModel:
        """Return the device model"""
        return self.__device

    @property
    def type(self) -> DeviceTypeEnum:
        """Return the device type"""
        return self.__device.type

    @property
    def connections(
        self,
    ) -> Dict[str, Union[NetconfConnectionModel, SshConnectionModel]]:
        """Return the device connections"""
        return self.__device.connections

    @property
    def connection_names(self) -> List[str]:
        """Return the device connection names"""
        return list(self.connections.keys())

    # @property
    # def connection_types(self) -> Dict[str, ConnectionTypeEnum]:
    #     """Return the device connection types"""
    #     return {k: v.type for k, v in self.connections.items()}

    def get_connection_params_by_type(self, type_name: str) -> List[
        Union[
            NetconfConnectionModel,
            SshConnectionModel,
            SmxRestConnectionModel,
            FtpConnectionModel,
        ]
    ]:
        """Return list of netconf connections"""
        return {k: v for k, v in self.connections.items() if v.type == type_name}

    def get_connection_params(self, name: str) -> Union[
        NetconfConnectionModel,
        SshConnectionModel,
        SmxRestConnectionModel,
        FtpConnectionModel,
    ]:
        """Return the dict of device connection parameters or None if not found"""
        connection_params = None
        if name in self.connection_names:
            connection_params = self.connections[name]
        return connection_params


class Devices:
    """Device class for all devices"""

    def __init__(self, fileobj: Union[str, IO]):
        self.__devices = self.__get_devices(fileobj)

    @property
    def devices(self) -> DevicesModel:
        """Return the devices model"""
        return self.__devices

    @property
    def device_names(self) -> List[str]:
        """Return the device names"""
        return list(self.devices.keys())

    def get_device(self, name: str) -> Device:
        """Return the device model or None if not found"""
        device_model = None
        if name in self.device_names:
            device_model = Device(self.devices[name])
        return device_model

    def __get_devices(self, fileobj: Union[str, IO]) -> Dict:
        """Return the validated device model"""
        data = self.__load_yaml_file(fileobj)
        if data is None or data == {}:
            raise DeviceCfgError("No data in devices yaml file.")
        if len(data.get("devices")) == 0:
            raise DeviceCfgError("No devices defined in devices yaml file.")
        return DevicesModel(**data).devices

    # TODO - future remove this method favoring device method
    def get_device_connection_params(
        self, name: str, connection_name: str
    ) -> Union[NetconfConnectionModel, SshConnectionModel, FtpConnectionModel]:
        """Return the device connection or None if not found"""
        device_connection_params_model = None
        device_model = self.get_device(name)
        if device_model:
            device_connection_params_model = device_model.get_connection_params(
                connection_name
            )
        return device_connection_params_model

    def __load_yaml_file(self, fileobj: Union[str, IO]) -> dict:
        """Return configuration file as dictionary."""
        try:
            # if fileobj is a string, open the file and load the yaml
            if isinstance(fileobj, str):
                with open(fileobj, "r", encoding="utf8") as devicesfile:
                    params = yaml.safe_load(devicesfile)
            else:
                # else assume fileobj is a file object and load the yaml
                params = yaml.safe_load(fileobj)
        except FileNotFoundError as err:
            # Should only hit when fileobj is a string
            time.sleep(1)
            raise DeviceCfgError(
                f"Cannot find file devices yaml file. err: {err}"
            ) from err
        except IOError as err:
            time.sleep(1)
            raise DeviceCfgError(
                f"Devices file I/O error({err.errno}): {err.strerror}  " f", err: {err}"
            ) from err
        except yaml.YAMLError as error:
            msg = "YAMLError Something went wrong while parsing params.yaml file."
            err_problem_mark = getattr(error, "problem_mark", None)
            if err_problem_mark is not None:
                err_context = getattr(error, "context", None)
                err_problem = getattr(error, "problem", None)
                msg += str(err_problem_mark) + "\n "
                msg += str(err_problem) + " "
                if err_context is not None:
                    msg += str(err_context)
                msg += "\nPlease correct data and retry."
            time.sleep(1)
            raise DeviceCfgError(msg) from error
        return params


if __name__ == "__main__":
    # Testing out the class as used by a CLI script
    DEVICES_FILE = "config/devices.yaml"

    # Example of running without the with statement (probably easier to use)
    devices = Devices(DEVICES_FILE)

    # Example of running using the with statement
    with open(DEVICES_FILE, "r", encoding="utf8") as infile:
        devices = Devices(infile)
        device_names = devices.device_names
        print(device_names)

    # ----- Sunny day scenarios

    # Example 1 of getting device connection
    if devices.get_device("simob") is not None:
        device = devices.get_device("simob")
        if device.get_connection_params("netconf") is not None:
            device_connection_parms = device.get_connection_params("netconf").dict()
            print(device_connection_parms)

    # Example 2 of getting device connection
    device = devices.get_device("simob")
    if device:
        device_connection_params = device.get_connection_params("netconf")
        if device_connection_params:
            print(device_connection_params)

    # Example 3 of getting device connection (preferred being easiest method)
    device_conn_params = devices.get_device_connection_params("simob", "netconf")
    device_conn_params_by_type = device.get_connection_params_by_type("netconf")
    print("connection type", device_conn_params.type)
    print("connection host", device_conn_params.host)

    # ----- Rainy day scenarios

    # device that doesn't exist returns None
    device_conn_params = devices.get_device_connection_params("not_present", "netconf")

    # device present but connection not present returns None
    device_conn_params = devices.get_device_connection_params("simob", "not_present")

    # device that doesn't exist returns None
    not_present_device = devices.get_device("not_present")

    # device present but connection not present returns None
    not_present_conn = devices.get_device("simob").get_connection_params("not_present")

    # device not present with connection not present triggers traceback
    # not_present_all = devices.get_device("not_present").get_connection_params(
    #     "not_present"
    # )
