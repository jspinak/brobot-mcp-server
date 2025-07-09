"""Basic tests for the Brobot client library."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from brobot_client import (
    BrobotClient,
    StateStructure, State, StateTransition,
    Observation, ActiveState,
    ActionResult, Location
)
from brobot_client.exceptions import BrobotActionError


class TestBrobotClient:
    """Test synchronous client functionality."""
    
    @pytest.fixture
    def mock_response(self):
        """Create a mock response object."""
        mock = Mock()
        mock.json.return_value = {}
        mock.raise_for_status = Mock()
        return mock
    
    @pytest.fixture
    def client(self):
        """Create a client instance."""
        return BrobotClient(base_url="http://test.local")
    
    def test_client_initialization(self):
        """Test client initialization."""
        client = BrobotClient(base_url="http://example.com", timeout=60.0)
        assert client.base_url == "http://example.com"
        assert client.api_base == "http://example.com/api/v1"
        assert client.timeout == 60.0
    
    @patch('requests.Session.request')
    def test_get_state_structure(self, mock_request, client, mock_response):
        """Test getting state structure."""
        # Mock response data
        mock_response.json.return_value = {
            "states": [
                {
                    "name": "main_menu",
                    "description": "Main menu",
                    "images": ["menu.png"],
                    "transitions": [
                        {
                            "from_state": "main_menu",
                            "to_state": "settings",
                            "action": "click_settings",
                            "probability": 0.95
                        }
                    ],
                    "is_initial": True,
                    "is_final": False
                }
            ],
            "current_state": "main_menu",
            "metadata": {"version": "1.0"}
        }
        mock_request.return_value = mock_response
        
        # Call method
        result = client.get_state_structure()
        
        # Verify
        assert isinstance(result, StateStructure)
        assert len(result.states) == 1
        assert result.states[0].name == "main_menu"
        assert len(result.states[0].transitions) == 1
        assert result.current_state == "main_menu"
    
    @patch('requests.Session.request')
    def test_get_observation(self, mock_request, client, mock_response):
        """Test getting observation."""
        # Mock response data
        mock_response.json.return_value = {
            "timestamp": "2024-01-20T10:30:00",
            "active_states": [
                {
                    "name": "dashboard",
                    "confidence": 0.95,
                    "matched_patterns": ["dashboard_header.png"]
                }
            ],
            "screenshot": "base64data",
            "screen_width": 1920,
            "screen_height": 1080,
            "metadata": {}
        }
        mock_request.return_value = mock_response
        
        # Call method
        result = client.get_observation()
        
        # Verify
        assert isinstance(result, Observation)
        assert len(result.active_states) == 1
        assert result.active_states[0].name == "dashboard"
        assert result.screen_width == 1920
        assert result.screenshot == "base64data"
    
    @patch('requests.Session.request')
    def test_click_with_pattern(self, mock_request, client, mock_response):
        """Test click action with image pattern."""
        # Mock response data
        mock_response.json.return_value = {
            "success": True,
            "action_type": "click",
            "duration": 0.5,
            "result_state": None,
            "error": None,
            "metadata": {}
        }
        mock_request.return_value = mock_response
        
        # Call method
        result = client.click(image_pattern="button.png", confidence=0.9)
        
        # Verify
        assert isinstance(result, ActionResult)
        assert result.success is True
        assert result.action_type == "click"
        
        # Check request was made correctly
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]['json']['action_type'] == 'click'
        assert call_args[1]['json']['parameters']['image_pattern'] == 'button.png'
    
    @patch('requests.Session.request')
    def test_click_with_location(self, mock_request, client, mock_response):
        """Test click action with location."""
        # Mock response data
        mock_response.json.return_value = {
            "success": True,
            "action_type": "click",
            "duration": 0.3,
            "result_state": None,
            "error": None,
            "metadata": {}
        }
        mock_request.return_value = mock_response
        
        # Call method
        location = Location(x=500, y=300)
        result = client.click(location=location)
        
        # Verify request parameters
        call_args = mock_request.call_args
        params = call_args[1]['json']['parameters']
        assert params['location'] == {'x': 500, 'y': 300}
    
    @patch('requests.Session.request')
    def test_action_failure(self, mock_request, client, mock_response):
        """Test handling of action failure."""
        # Mock failed response
        mock_response.json.return_value = {
            "success": False,
            "action_type": "click",
            "duration": 0.1,
            "result_state": None,
            "error": "Pattern not found",
            "metadata": {"searched_area": "full_screen"}
        }
        mock_request.return_value = mock_response
        
        # Call should raise exception
        with pytest.raises(BrobotActionError) as exc_info:
            client.click(image_pattern="nonexistent.png")
        
        # Verify exception details
        assert "Pattern not found" in str(exc_info.value)
        assert exc_info.value.action_type == "click"
        assert exc_info.value.error_details["searched_area"] == "full_screen"
    
    def test_context_manager(self):
        """Test client works as context manager."""
        with BrobotClient() as client:
            assert client.session is not None
        
        # Session should be closed after context
        assert client.session._closed is True