"""
SSH related errors
"""

from app.lib.errors_base import ToolboxError


class SshAuthenticationError(ToolboxError):
    """Session cannot be established due to authentication failure"""
