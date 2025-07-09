"""Data models for the Brobot client library."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class StateTransition:
    """Represents a transition between states."""
    from_state: str
    to_state: str
    action: str
    probability: float = 0.0


@dataclass
class State:
    """Represents a single state in the application."""
    name: str
    description: str = ""
    images: List[str] = field(default_factory=list)
    transitions: List[StateTransition] = field(default_factory=list)
    is_initial: bool = False
    is_final: bool = False


@dataclass
class StateStructure:
    """Complete state structure of the application."""
    states: List[State]
    current_state: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ActiveState:
    """Information about an active state."""
    name: str
    confidence: float
    matched_patterns: List[str] = field(default_factory=list)


@dataclass
class Observation:
    """Current observation of the application."""
    timestamp: datetime
    active_states: List[ActiveState]
    screenshot: Optional[str] = None
    screen_width: int = 0
    screen_height: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_most_confident_state(self) -> Optional[ActiveState]:
        """Get the active state with highest confidence."""
        if not self.active_states:
            return None
        return max(self.active_states, key=lambda s: s.confidence)
    
    def save_screenshot(self, filepath: str) -> bool:
        """Save the screenshot to a file."""
        if not self.screenshot:
            return False
        
        import base64
        try:
            image_data = base64.b64decode(self.screenshot)
            with open(filepath, 'wb') as f:
                f.write(image_data)
            return True
        except Exception:
            return False


@dataclass
class Location:
    """Screen location coordinates."""
    x: int
    y: int
    
    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y}


@dataclass
class Region:
    """Screen region definition."""
    x: int
    y: int
    width: int
    height: int
    
    def to_dict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height
        }
    
    @property
    def center(self) -> Location:
        """Get the center point of the region."""
        return Location(
            x=self.x + self.width // 2,
            y=self.y + self.height // 2
        )


@dataclass
class ActionRequest:
    """Request to execute an action."""
    action_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    target_state: Optional[str] = None
    timeout: float = 10.0
    
    def to_dict(self) -> dict:
        return {
            "action_type": self.action_type,
            "parameters": self.parameters,
            "target_state": self.target_state,
            "timeout": self.timeout
        }


@dataclass
class ActionResult:
    """Result of an executed action."""
    success: bool
    action_type: str
    duration: float
    result_state: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)