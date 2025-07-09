"""
Brobot MCP Client Library

A Python client library for interacting with the Brobot MCP Server.
"""

from .client import BrobotClient
from .async_client import AsyncBrobotClient
from .exceptions import (
    BrobotClientError,
    BrobotConnectionError,
    BrobotTimeoutError,
    BrobotActionError
)
from .models import (
    StateStructure,
    State,
    StateTransition,
    Observation,
    ActiveState,
    ActionRequest,
    ActionResult,
    Location,
    Region
)

__version__ = "0.1.0"
__all__ = [
    "BrobotClient",
    "AsyncBrobotClient",
    "BrobotClientError",
    "BrobotConnectionError", 
    "BrobotTimeoutError",
    "BrobotActionError",
    "StateStructure",
    "State",
    "StateTransition",
    "Observation",
    "ActiveState",
    "ActionRequest",
    "ActionResult",
    "Location",
    "Region"
]