"""Synchronous client for the Brobot MCP Server."""

import requests
from typing import Dict, Any, Optional, Union
from datetime import datetime
import logging
from urllib.parse import urljoin

from .models import (
    StateStructure, State, StateTransition,
    Observation, ActiveState,
    ActionRequest, ActionResult,
    Location, Region
)
from .exceptions import (
    BrobotClientError,
    BrobotConnectionError,
    BrobotTimeoutError,
    BrobotActionError
)

logger = logging.getLogger(__name__)


class BrobotClient:
    """Synchronous client for interacting with the Brobot MCP Server."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: float = 30.0,
        verify_ssl: bool = True
    ):
        """
        Initialize the Brobot client.
        
        Args:
            base_url: Base URL of the MCP server
            timeout: Default timeout for requests in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api/v1"
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close session."""
        self.close()
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the server.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            json_data: JSON data for request body
            timeout: Request timeout (uses default if None)
            
        Returns:
            Response data as dictionary
            
        Raises:
            BrobotConnectionError: If unable to connect
            BrobotTimeoutError: If request times out
            BrobotClientError: For other errors
        """
        url = urljoin(self.api_base, endpoint.lstrip('/'))
        timeout = timeout or self.timeout
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=json_data,
                timeout=timeout,
                verify=self.verify_ssl
            )
            
            # Raise for HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            return response.json()
            
        except requests.exceptions.ConnectionError as e:
            raise BrobotConnectionError(f"Failed to connect to server at {url}: {e}")
        except requests.exceptions.Timeout as e:
            raise BrobotTimeoutError(f"Request timed out after {timeout}s: {e}")
        except requests.exceptions.HTTPError as e:
            # Try to get error details from response
            try:
                error_data = e.response.json()
                detail = error_data.get("detail", str(e))
            except:
                detail = str(e)
            raise BrobotClientError(f"HTTP error: {detail}")
        except Exception as e:
            raise BrobotClientError(f"Unexpected error: {e}")
    
    def get_state_structure(self) -> StateStructure:
        """
        Get the application state structure.
        
        Returns:
            StateStructure object
        """
        data = self._make_request("GET", "/state_structure")
        
        # Convert to model objects
        states = []
        for state_data in data.get("states", []):
            transitions = [
                StateTransition(
                    from_state=t["from_state"],
                    to_state=t["to_state"],
                    action=t["action"],
                    probability=t.get("probability", 0.0)
                )
                for t in state_data.get("transitions", [])
            ]
            
            state = State(
                name=state_data["name"],
                description=state_data.get("description", ""),
                images=state_data.get("images", []),
                transitions=transitions,
                is_initial=state_data.get("is_initial", False),
                is_final=state_data.get("is_final", False)
            )
            states.append(state)
        
        return StateStructure(
            states=states,
            current_state=data.get("current_state"),
            metadata=data.get("metadata", {})
        )
    
    def get_observation(self) -> Observation:
        """
        Get current observation of the application.
        
        Returns:
            Observation object
        """
        data = self._make_request("GET", "/observation")
        
        # Convert to model objects
        active_states = [
            ActiveState(
                name=s["name"],
                confidence=s["confidence"],
                matched_patterns=s.get("matched_patterns", [])
            )
            for s in data.get("active_states", [])
        ]
        
        # Parse timestamp
        timestamp = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
        
        return Observation(
            timestamp=timestamp,
            active_states=active_states,
            screenshot=data.get("screenshot"),
            screen_width=data.get("screen_width", 0),
            screen_height=data.get("screen_height", 0),
            metadata=data.get("metadata", {})
        )
    
    def execute_action(
        self,
        action_type: str,
        parameters: Optional[Dict[str, Any]] = None,
        target_state: Optional[str] = None,
        timeout: Optional[float] = None
    ) -> ActionResult:
        """
        Execute an automation action.
        
        Args:
            action_type: Type of action (click, type, drag, etc.)
            parameters: Action-specific parameters
            target_state: Expected state after action
            timeout: Action timeout in seconds
            
        Returns:
            ActionResult object
            
        Raises:
            BrobotActionError: If action execution fails
        """
        request = ActionRequest(
            action_type=action_type,
            parameters=parameters or {},
            target_state=target_state,
            timeout=timeout or self.timeout
        )
        
        data = self._make_request("POST", "/execute", json_data=request.to_dict())
        
        result = ActionResult(
            success=data["success"],
            action_type=data["action_type"],
            duration=data["duration"],
            result_state=data.get("result_state"),
            error=data.get("error"),
            metadata=data.get("metadata", {})
        )
        
        # Raise error if action failed
        if not result.success:
            raise BrobotActionError(
                f"Action '{action_type}' failed: {result.error}",
                action_type=action_type,
                error_details=result.metadata
            )
        
        return result
    
    # Convenience methods for common actions
    
    def click(
        self,
        image_pattern: Optional[str] = None,
        location: Optional[Location] = None,
        confidence: float = 0.9,
        timeout: Optional[float] = None
    ) -> ActionResult:
        """
        Click on an image pattern or location.
        
        Args:
            image_pattern: Image file to search for
            location: Alternative to image_pattern, specific coordinates
            confidence: Minimum confidence score for pattern matching
            timeout: Action timeout
            
        Returns:
            ActionResult object
        """
        parameters = {}
        
        if image_pattern:
            parameters["image_pattern"] = image_pattern
            parameters["confidence"] = confidence
        elif location:
            parameters["location"] = location.to_dict()
        else:
            raise ValueError("Either image_pattern or location must be provided")
        
        return self.execute_action("click", parameters, timeout=timeout)
    
    def type_text(
        self,
        text: str,
        typing_speed: Optional[int] = None,
        timeout: Optional[float] = None
    ) -> ActionResult:
        """
        Type text at current cursor location.
        
        Args:
            text: Text to type
            typing_speed: Characters per minute (optional)
            timeout: Action timeout
            
        Returns:
            ActionResult object
        """
        parameters = {"text": text}
        
        if typing_speed is not None:
            parameters["typing_speed"] = typing_speed
        
        return self.execute_action("type", parameters, timeout=timeout)
    
    def drag(
        self,
        start: Union[Location, str],
        end: Union[Location, str],
        duration: float = 1.0,
        timeout: Optional[float] = None
    ) -> ActionResult:
        """
        Drag from one location to another.
        
        Args:
            start: Starting location or image pattern
            end: Ending location or image pattern
            duration: Drag duration in seconds
            timeout: Action timeout
            
        Returns:
            ActionResult object
        """
        parameters = {"duration": duration}
        
        # Handle start position
        if isinstance(start, Location):
            parameters["start_x"] = start.x
            parameters["start_y"] = start.y
        else:
            parameters["start_pattern"] = start
        
        # Handle end position
        if isinstance(end, Location):
            parameters["end_x"] = end.x
            parameters["end_y"] = end.y
        else:
            parameters["end_pattern"] = end
        
        return self.execute_action("drag", parameters, timeout=timeout)
    
    def wait_for_state(
        self,
        state_name: str,
        timeout: float = 30.0
    ) -> ActionResult:
        """
        Wait for a specific state to become active.
        
        Args:
            state_name: Name of the state to wait for
            timeout: Maximum wait time in seconds
            
        Returns:
            ActionResult object
        """
        parameters = {
            "state_name": state_name,
            "check_interval": 1.0
        }
        
        return self.execute_action("wait", parameters, target_state=state_name, timeout=timeout)
    
    def get_health(self) -> Dict[str, Any]:
        """
        Get server health status.
        
        Returns:
            Health status dictionary
        """
        return self._make_request("GET", "/health")