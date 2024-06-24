"""
Base Class for SSH Protocol

Initialling testing with AXOS devices

Connection methods are based on AsyncSSH and should be running in asyncio loop

Strongly influenced by work from: https://github.com/selfuryon/netdev

# TODO consider enabling debug logging - calling app should set logging level
"""

import asyncio
import re

import asyncssh

from app.lib.protocol_base.ssh.errors import SshAuthenticationError


class BaseDevice:
    """Base Abstract class for SSH devices"""

    def __init__(
        self,
        hostname: str,
        username: str,
        password: str,
        device_type: str,
        port: int = 22,
        timeout: int = 30,
        pattern: str = r"\S+#",
    ) -> None:
        """Initialize the BaseDevice object
        :param hostname: Hostname or IP address of device
        :param username: Username to authenticate with
        :param password: Password to authenticate with
        :param device_type: Device type
        :param port: TCP port to connect to
        :param timeout: Timeout in seconds
        """
        self._hostname = hostname
        self._port = int(port)
        self._device_type = device_type
        self._timeout = int(timeout)
        self._pattern = pattern
        self._loop = asyncio.get_event_loop()

        # Connection parms to dictionary
        self._conn_params_dict = {
            "host": self._hostname,
            "port": self._port,
            "username": username,
            "password": password,
            "known_hosts": None,  # Disable host key checking
        }

        # Initialize other attributes
        self.stdin = self.stdout = self.stderr = self._conn = None
        self._base_prompt = self._base_pattern = ""
        self._MAX_BUFFER = 65535
        self._ansi_escape_codes = False

    @property
    def base_prompt(self) -> str:
        """Return base prompt for device"""
        return self._base_prompt

    async def __aenter__(self) -> "BaseDevice":
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit"""
        await self.disconnect()

    async def connect(self) -> None:
        """Establishing SSH connection to device"""
        await self._establish_connection()
        await self._set_base_prompt()

    async def _establish_connection(self) -> None:
        """Establish SSH connection to the network device
        Timeout will generate a asyncio.TimeoutError
        Authentication failed will generate a asyncssh.misc.PermissionDenied
        """
        try:
            self._conn = await asyncssh.connect(**self._conn_params_dict)
        except asyncssh.misc.PermissionDenied as err:
            raise SshAuthenticationError(
                f"Failed to connect to {self.hostname}:{self.port}:{err}"
            ) from err

        self._stdin, self._stdout, self._stderr = await self._conn.open_session(
            term_type="Dumb", term_size=(200, 24)
        )

        # Flush unnecessary data
        delimiters = map(re.escape, type(self)._delimiters)
        delimiters = r"|".join(delimiters)
        output = await self._read_until_pattern(delimiters=delimiters)
        return output

        # async def _set_base_prompt(self) -> None:
        """Set base_prompt and base_pattern
        
        base_prompt - usually hostname
        base_pattern - pattern to terminate read when base_prompt is detected
        
        For AXOS devices base pattern is "prompt(\(.*?\))?[#|>]"
        """
