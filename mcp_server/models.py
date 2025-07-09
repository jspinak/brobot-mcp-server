"""Pydantic models for MCP API request and response schemas."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class StateTransition(BaseModel):
    """Represents a transition between states."""
    from_state: str = Field(..., description="Source state name")
    to_state: str = Field(..., description="Target state name")
    action: str = Field(..., description="Action that triggers this transition")
    probability: float = Field(0.0, ge=0.0, le=1.0, description="Transition probability")


class State(BaseModel):
    """Represents a single state in the application state structure."""
    name: str = Field(..., description="Unique state name")
    description: Optional[str] = Field(None, description="State description")
    images: List[str] = Field(default_factory=list, description="List of image patterns associated with this state")
    transitions: List[StateTransition] = Field(default_factory=list, description="Possible transitions from this state")
    is_initial: bool = Field(False, description="Whether this is an initial state")
    is_final: bool = Field(False, description="Whether this is a final state")


class StateStructure(BaseModel):
    """Complete state structure of the application."""
    states: List[State] = Field(..., description="List of all states")
    current_state: Optional[str] = Field(None, description="Currently active state name")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ActiveState(BaseModel):
    """Information about an active state."""
    name: str = Field(..., description="State name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    matched_patterns: List[str] = Field(default_factory=list, description="Patterns that matched")


class Observation(BaseModel):
    """Current observation of the application."""
    timestamp: datetime = Field(..., description="Observation timestamp")
    active_states: List[ActiveState] = Field(..., description="Currently active states")
    screenshot: Optional[str] = Field(None, description="Base64 encoded screenshot")
    screen_width: int = Field(..., description="Screen width in pixels")
    screen_height: int = Field(..., description="Screen height in pixels")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional observation data")


class Location(BaseModel):
    """Screen location coordinates."""
    x: int = Field(..., description="X coordinate")
    y: int = Field(..., description="Y coordinate")


class Region(BaseModel):
    """Screen region definition."""
    x: int = Field(..., description="X coordinate of top-left corner")
    y: int = Field(..., description="Y coordinate of top-left corner")
    width: int = Field(..., description="Region width")
    height: int = Field(..., description="Region height")


class ActionRequest(BaseModel):
    """Request to execute an action."""
    action_type: str = Field(..., description="Type of action (click, type, drag, etc.)")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action-specific parameters")
    target_state: Optional[str] = Field(None, description="Expected state after action")
    timeout: float = Field(10.0, gt=0, description="Action timeout in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "action_type": "click",
                "parameters": {
                    "image_pattern": "button_submit.png",
                    "confidence": 0.9
                },
                "target_state": "form_submitted",
                "timeout": 5.0
            }
        }


class ActionResult(BaseModel):
    """Result of an executed action."""
    success: bool = Field(..., description="Whether the action succeeded")
    action_type: str = Field(..., description="Type of action executed")
    duration: float = Field(..., description="Execution duration in seconds")
    result_state: Optional[str] = Field(None, description="State after action execution")
    error: Optional[str] = Field(None, description="Error message if action failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional result data")


class HealthStatus(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Server status")
    version: str = Field(..., description="Server version")
    brobot_connected: bool = Field(False, description="Whether Brobot CLI is accessible")
    timestamp: datetime = Field(default_factory=datetime.now, description="Status check timestamp")