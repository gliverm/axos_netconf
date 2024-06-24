"""
Netconf session errors
"""


class NetconfSessionError(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message):
        super().__init__(message)
        self.__message = message

    @property
    def message(self):
        """Return the message"""
        return self.__message

    def __str__(self):
        """Override returns message attribute as string representation of object."""
        return self.__message


class NetconfAuthenticationError(NetconfSessionError):
    """Session cannot be established due to authentication failure"""
