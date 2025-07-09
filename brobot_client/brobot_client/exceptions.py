"""Exception classes for the Brobot client library."""


class BrobotClientError(Exception):
    """Base exception for all Brobot client errors."""
    pass


class BrobotConnectionError(BrobotClientError):
    """Raised when unable to connect to the Brobot MCP server."""
    pass


class BrobotTimeoutError(BrobotClientError):
    """Raised when a request times out."""
    pass


class BrobotActionError(BrobotClientError):
    """Raised when an action execution fails."""
    
    def __init__(self, message: str, action_type: str = None, error_details: dict = None):
        super().__init__(message)
        self.action_type = action_type
        self.error_details = error_details or {}


class BrobotValidationError(BrobotClientError):
    """Raised when request validation fails."""
    pass