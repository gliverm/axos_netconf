"""
Core set of Netconf session operations.  

Design choices:
* known issue with ncclient create_subscription with using filters
* All create_subscription functions will use dispatch

"""

import ncclient
from ncclient.operations import RPCError
from ncclient import manager
from lxml import etree

from lib.axos_netconf.errors import NetconfAuthenticationError, NetconfSessionError
from lib.axos_netconf.responses import NetconfResponse


class NetconfSessionMixin:
    """Class to represent a netconf session.  The class will attempt to
    be a base class for all netconf functions.  The class will be
    a wrapper around the ncclient.manager class.
    """

    def __init__(self, hostname, port, timeout, username, password, devicename=None):
        self.hostname = hostname
        self.port = port
        self.timeout = timeout
        self.retry = 3
        self.username = username
        self.password = password
        self.session = None
        self.devicename = devicename

    def connect(self, retry=True):
        """Attempt to establish a netconf session.  If retry is True, then
        the connect function will attempt to connect to the device up to
        the number of times specified by the retry attribute.  If retry is
        false, then the connect function will attempt to connect to the
        to the device once.  If the connection fails, then the connect
        session will raise a NetconfSessionError exception.
        """
        if retry:
            retry = 0
        else:
            retry = self.retry - 1

        while retry < self.retry:
            try:
                # allow_agents = False when authentication via username/password
                self.session = manager.connect(
                    host=self.hostname,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    hostkey_verify=False,
                    timeout=self.timeout,
                    allow_agent=False,
                    device_params={"name": "default"},
                )
                break
            except ncclient.transport.AuthenticationError as err:
                self.session = None
                raise NetconfAuthenticationError(
                    f"Failed to connect to device: {err}"
                ) from err
            except ncclient.transport.SSHError as err:
                if retry < self.retry:
                    retry += 1
                    if retry == self.retry:
                        raise NetconfSessionError(
                            f"Failed to connect to device: {err}.  "
                            f"Retried {retry} times."
                        ) from err
                    continue
                self.session = None
            except Exception as err:
                self.session = None
                raise NetconfSessionError(
                    f"Failed to connect to device: {err}"
                ) from err
        return self.session

    def disconnect(self):
        """Close the netconf session"""
        if self.session is not None:
            self.session.close_session()
            self.session = None

    def __enter__(self):
        """Context manager establish a netconf session"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager disconnect the netconf session"""
        return self.disconnect()

    def __check_session_connected(self):
        """Check if the session is connected.  If the session is not connected,
        then attempt to reconnect to the device.  If the session is still not
        connected, then raise a NetconfSessionError exception.
        """

        if self.session is None or not self.session.connected:
            try:
                self.session.connect()
            except Exception as err:
                raise NetconfSessionError(
                    f"Failed to reconnect to device: {err}"
                ) from err

    def get_config(self, nc_filter=None):
        """Get the running config from the device.  If filter is not None,
        get the config based on the filter.  The filter may be a
        subtree filter or an xpath filter."""

        self.__check_session_connected()

        try:
            response = self.session.get_config(
                "running", filter=nc_filter, with_defaults="report-all"
            )
            return response
        except Exception as err:
            raise NetconfSessionError(f"Netconf get-config failed: {err}") from err

    def get(self, nc_filter=None):
        """Get from the device.  This is not for use for configuration.  If filter
        is not None get the config based on the filter.  The filter may be a
        subtree filter or an xpath filter."""
        self.__check_session_connected()

        try:
            response = self.session.get(filter=nc_filter)
            return response
        except Exception as err:
            raise NetconfSessionError(f"Netconf get failed: {err}") from err

    def edit_config(self, config):
        """Edit the running config on the device."""

        self.__check_session_connected()

        try:
            self.session.edit_config(config, target="running")
            return NetconfResponse()
        except RPCError as err:
            return NetconfResponse(False, err.args[0])
        except Exception as err:
            raise NetconfSessionError(f"Netconf edit-config failed: {err}") from err

    def dispatch(self, rpc_command):
        """Dispatch an RPC execute command to the device."""

        self.__check_session_connected()

        try:
            response = self.session.dispatch(
                rpc_command=(etree.fromstring(rpc_command))
            )
            return NetconfResponse(xml=response.xml)
        except RPCError as err:
            return NetconfResponse(ok=False, err=err.args[0])
        except Exception as err:
            raise NetconfSessionError(f"Netconf dispatch failed: {err}") from err

    def take_session_notification(self, block=False, timeout=30):
        """Attempt to retrieve notification from queue of received notifications."""

        self.__check_session_connected()

        try:
            response = self.session.take_notification(block=block, timeout=timeout)
            if response is None:
                return NetconfResponse()
            return NetconfResponse(xml=response.notification_xml)
        except RPCError as err:
            return NetconfResponse(ok=False, err=err.args[0])
        except Exception as err:
            raise NetconfSessionError(
                f"Netconf take_notification failed: {err}"
            ) from err
