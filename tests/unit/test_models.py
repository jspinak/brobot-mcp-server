"""Unit tests for Pydantic models."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from mcp_server.models import (
    StateTransition,
    State,
    StateStructure,
    ActiveState,
    Observation,
    Location,
    Region,
    ActionRequest,
    ActionResult,
    HealthStatus
)


class TestStateModels:
    """Test state-related models."""
    
    def test_state_transition_creation(self):
        """Test StateTransition model creation."""
        transition = StateTransition(
            from_state="login",
            to_state="dashboard",
            action="submit_login",
            probability=0.95
        )
        
        assert transition.from_state == "login"
        assert transition.to_state == "dashboard"
        assert transition.action == "submit_login"
        assert transition.probability == 0.95
    
    def test_state_transition_validation(self):
        """Test StateTransition validation."""
        # Test probability bounds
        with pytest.raises(ValidationError):
            StateTransition(
                from_state="a",
                to_state="b",
                action="test",
                probability=1.5  # Invalid: > 1.0
            )
        
        with pytest.raises(ValidationError):
            StateTransition(
                from_state="a",
                to_state="b",
                action="test",
                probability=-0.1  # Invalid: < 0.0
            )
    
    def test_state_creation(self):
        """Test State model creation."""
        transitions = [
            StateTransition(
                from_state="menu",
                to_state="settings",
                action="click_settings",
                probability=0.9
            )
        ]
        
        state = State(
            name="menu",
            description="Main menu",
            images=["menu.png", "logo.png"],
            transitions=transitions,
            is_initial=True,
            is_final=False
        )
        
        assert state.name == "menu"
        assert state.description == "Main menu"
        assert len(state.images) == 2
        assert len(state.transitions) == 1
        assert state.is_initial is True
        assert state.is_final is False
    
    def test_state_defaults(self):
        """Test State model defaults."""
        state = State(name="test_state")
        
        assert state.name == "test_state"
        assert state.description is None
        assert state.images == []
        assert state.transitions == []
        assert state.is_initial is False
        assert state.is_final is False
    
    def test_state_structure_creation(self):
        """Test StateStructure model creation."""
        states = [
            State(name="state1"),
            State(name="state2")
        ]
        
        structure = StateStructure(
            states=states,
            current_state="state1",
            metadata={"version": "1.0"}
        )
        
        assert len(structure.states) == 2
        assert structure.current_state == "state1"
        assert structure.metadata["version"] == "1.0"


class TestObservationModels:
    """Test observation-related models."""
    
    def test_active_state_creation(self):
        """Test ActiveState model creation."""
        active_state = ActiveState(
            name="dashboard",
            confidence=0.85,
            matched_patterns=["dashboard_header.png", "user_menu.png"]
        )
        
        assert active_state.name == "dashboard"
        assert active_state.confidence == 0.85
        assert len(active_state.matched_patterns) == 2
    
    def test_active_state_validation(self):
        """Test ActiveState validation."""
        # Test confidence bounds
        with pytest.raises(ValidationError):
            ActiveState(name="test", confidence=1.1)  # > 1.0
        
        with pytest.raises(ValidationError):
            ActiveState(name="test", confidence=-0.1)  # < 0.0
    
    def test_observation_creation(self):
        """Test Observation model creation."""
        active_states = [
            ActiveState(name="main", confidence=0.9),
            ActiveState(name="sidebar", confidence=0.8)
        ]
        
        obs = Observation(
            timestamp=datetime.now(),
            active_states=active_states,
            screenshot="base64data",
            screen_width=1920,
            screen_height=1080,
            metadata={"capture_time": 0.1}
        )
        
        assert len(obs.active_states) == 2
        assert obs.screenshot == "base64data"
        assert obs.screen_width == 1920
        assert obs.screen_height == 1080
        assert obs.metadata["capture_time"] == 0.1


class TestLocationModels:
    """Test location-related models."""
    
    def test_location_creation(self):
        """Test Location model creation."""
        loc = Location(x=100, y=200)
        
        assert loc.x == 100
        assert loc.y == 200
    
    def test_region_creation(self):
        """Test Region model creation."""
        region = Region(x=10, y=20, width=300, height=400)
        
        assert region.x == 10
        assert region.y == 20
        assert region.width == 300
        assert region.height == 400


class TestActionModels:
    """Test action-related models."""
    
    def test_action_request_creation(self):
        """Test ActionRequest model creation."""
        request = ActionRequest(
            action_type="click",
            parameters={"image_pattern": "button.png"},
            target_state="next_screen",
            timeout=5.0
        )
        
        assert request.action_type == "click"
        assert request.parameters["image_pattern"] == "button.png"
        assert request.target_state == "next_screen"
        assert request.timeout == 5.0
    
    def test_action_request_defaults(self):
        """Test ActionRequest defaults."""
        request = ActionRequest(action_type="wait")
        
        assert request.action_type == "wait"
        assert request.parameters == {}
        assert request.target_state is None
        assert request.timeout == 10.0  # Default timeout
    
    def test_action_request_validation(self):
        """Test ActionRequest validation."""
        # Test timeout validation
        with pytest.raises(ValidationError):
            ActionRequest(action_type="test", timeout=-1.0)  # Negative timeout
    
    def test_action_result_creation(self):
        """Test ActionResult model creation."""
        result = ActionResult(
            success=True,
            action_type="click",
            duration=0.5,
            result_state="dashboard",
            error=None,
            metadata={"click_position": {"x": 100, "y": 200}}
        )
        
        assert result.success is True
        assert result.action_type == "click"
        assert result.duration == 0.5
        assert result.result_state == "dashboard"
        assert result.error is None
        assert result.metadata["click_position"]["x"] == 100
    
    def test_action_result_with_error(self):
        """Test ActionResult with error."""
        result = ActionResult(
            success=False,
            action_type="click",
            duration=0.1,
            result_state=None,
            error="Pattern not found",
            metadata={"searched_area": "full_screen"}
        )
        
        assert result.success is False
        assert result.error == "Pattern not found"
        assert result.result_state is None


class TestHealthModels:
    """Test health-related models."""
    
    def test_health_status_creation(self):
        """Test HealthStatus model creation."""
        health = HealthStatus(
            status="ok",
            version="0.1.0",
            brobot_connected=True,
            timestamp=datetime.now()
        )
        
        assert health.status == "ok"
        assert health.version == "0.1.0"
        assert health.brobot_connected is True
        assert isinstance(health.timestamp, datetime)
    
    def test_health_status_defaults(self):
        """Test HealthStatus defaults."""
        health = HealthStatus(
            status="degraded",
            version="0.1.0"
        )
        
        assert health.status == "degraded"
        assert health.brobot_connected is False  # Default
        assert isinstance(health.timestamp, datetime)  # Auto-generated


class TestModelSerialization:
    """Test model serialization/deserialization."""
    
    def test_state_structure_serialization(self):
        """Test StateStructure JSON serialization."""
        structure = StateStructure(
            states=[State(name="test")],
            current_state="test",
            metadata={"key": "value"}
        )
        
        # Serialize to dict
        data = structure.model_dump()
        assert data["current_state"] == "test"
        assert len(data["states"]) == 1
        
        # Serialize to JSON
        json_str = structure.model_dump_json()
        assert '"current_state":"test"' in json_str
    
    def test_observation_deserialization(self):
        """Test Observation JSON deserialization."""
        json_data = {
            "timestamp": "2024-01-20T10:30:00",
            "active_states": [
                {
                    "name": "main",
                    "confidence": 0.9,
                    "matched_patterns": ["main.png"]
                }
            ],
            "screenshot": "base64data",
            "screen_width": 1920,
            "screen_height": 1080,
            "metadata": {}
        }
        
        obs = Observation.model_validate(json_data)
        assert obs.active_states[0].name == "main"
        assert obs.screenshot == "base64data"
    
    def test_action_request_example(self):
        """Test ActionRequest Config.schema_extra example."""
        # Get the example from the schema
        schema = ActionRequest.model_json_schema()
        example = schema.get("examples", [{}])[0] if "examples" in schema else ActionRequest.Config.schema_extra["example"]
        
        # Validate the example
        request = ActionRequest.model_validate(example)
        assert request.action_type == "click"
        assert request.parameters["image_pattern"] == "button_submit.png"