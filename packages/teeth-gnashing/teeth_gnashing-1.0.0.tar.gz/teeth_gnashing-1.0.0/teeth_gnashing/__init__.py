"""
teeth-gnashing: Production-ready Python library for dynamic snapshot-based encryption
using server-client architecture.
"""

__version__ = "1.0.0"
__author__ = "Kirill Nikitenko"
__license__ = "GPL-2.0"

from .client import (
    CryptoClient,
    CryptoConfig,
    CryptoError,
    AuthenticationError,
    SnapshotError,
)
from .server import (
    CryptoServer,
    ServerConfig,
)

__all__ = [
    "CryptoClient",
    "CryptoConfig",
    "CryptoServer",
    "ServerConfig",
    "CryptoError",
    "AuthenticationError",
    "SnapshotError",
]
