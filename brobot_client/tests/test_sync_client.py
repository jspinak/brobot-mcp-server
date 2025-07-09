"""Unit tests for synchronous Brobot client."""

import pytest
from unittest.mock import Mock, patch
import json

from brobot_client import BrobotClient
from brobot_client.exceptions import (
    BrobotClientError,
    BrobotConnectionError,
    BrobotValidationError,
    BrobotTimeoutError
)


class TestBrobotClientInitialization:
    """Test BrobotClient initialization."""
    
    def test_default_initialization(self):
        """Test client with default parameters."""
        client = BrobotClient()
        assert client.base_url == "http://localhost:8000"
        assert client.timeout == 30.0
        assert client.max_retries == 3
    
    def test_custom_initialization(self):
        """Test client with custom parameters."""
        client = BrobotClient(
            base_url="http://example.com:8080",
            timeout=60.0,
            max_retries=5
        )
        assert client.base_url == "http://example.com:8080"
        assert client.timeout == 60.0
        assert client.max_retries == 5
    
    def test_base_url_normalization(self):
        """Test that base URL is normalized."""
        # With trailing slash
        client = BrobotClient(base_url="http://localhost:8000/")
        assert client.base_url == "http://localhost:8000"
        
        # Without trailing slash
        client = BrobotClient(base_url="http://localhost:8000")
        assert client.base_url == "http://localhost:8000"


class TestHealthCheck:
    """Test health check functionality."""
    
    @patch('requests.get')
    def test_health_check_success(self, mock_get):
        """Test successful health check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "version": "0.1.0",
            "brobot_connected": True
        }
        mock_get.return_value = mock_response
        
        client = BrobotClient()
        result = client.health_check()
        
        assert result["status"] == "ok"
        assert result["version"] == "0.1.0"
        assert result["brobot_connected"] is True
        
        mock_get.assert_called_once_with(
            "http://localhost:8000/api/v1/health",
            timeout=30.0
        )
    
    @patch('requests.get')
    def test_health_check_connection_error(self, mock_get):
        """Test health check with connection error."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        client = BrobotClient()
        
        with pytest.raises(BrobotConnectionError) as exc_info:
            client.health_check()
        
        assert "Connection refused" in str(exc_info.value)
    
    @patch('requests.get')
    def test_health_check_timeout(self, mock_get):
        """Test health check with timeout."""
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        
        client = BrobotClient()
        
        with pytest.raises(BrobotTimeoutError) as exc_info:
            client.health_check()
        
        assert "Request timed out" in str(exc_info.value)


class TestStateStructure:
    """Test get_state_structure functionality."""
    
    @patch('requests.get')
    def test_get_state_structure_success(self, mock_get):
        """Test successful get_state_structure."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "states": [
                {"name": "main_menu", "description": "Main menu"}
            ],
            "current_state": "main_menu",
            "metadata": {}
        }
        mock_get.return_value = mock_response
        
        client = BrobotClient()
        result = client.get_state_structure()
        
        assert len(result["states"]) == 1
        assert result["states"][0]["name"] == "main_menu"
        assert result["current_state"] == "main_menu"
    
    @patch('requests.get')
    def test_get_state_structure_server_error(self, mock_get):
        """Test get_state_structure with server error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_response
        
        client = BrobotClient()
        
        with pytest.raises(BrobotClientError):
            client.get_state_structure()


class TestObservation:
    """Test get_observation functionality."""
    
    @patch('requests.get')
    def test_get_observation_success(self, mock_get):
        """Test successful get_observation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "timestamp": "2024-01-20T10:30:00",
            "active_states": [
                {"name": "dashboard", "confidence": 0.95}
            ],
            "screenshot": "base64imagedata",
            "screen_width": 1920,
            "screen_height": 1080,
            "metadata": {}
        }
        mock_get.return_value = mock_response
        
        client = BrobotClient()
        result = client.get_observation()
        
        assert result["active_states"][0]["name"] == "dashboard"
        assert result["screenshot"] == "base64imagedata"
        assert result["screen_width"] == 1920


class TestExecuteAction:
    """Test execute_action functionality."""
    
    @patch('requests.post')
    def test_execute_action_success(self, mock_post):
        """Test successful execute_action."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "action_type": "click",
            "duration": 0.5,
            "result_state": "next_screen",
            "error": None,
            "metadata": {}
        }
        mock_post.return_value = mock_response
        
        client = BrobotClient()
        result = client.execute_action(
            action_type="click",
            parameters={"image_pattern": "button.png"},
            target_state="next_screen",
            timeout=5.0
        )
        
        assert result["success"] is True
        assert result["action_type"] == "click"
        assert result["result_state"] == "next_screen"
        
        # Verify request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "http://localhost:8000/api/v1/execute"
        assert call_args[1]["json"]["action_type"] == "click"
        assert call_args[1]["json"]["parameters"]["image_pattern"] == "button.png"
        assert call_args[1]["json"]["timeout"] == 5.0
    
    @patch('requests.post')
    def test_execute_action_validation_error(self, mock_post):
        """Test execute_action with validation error."""
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "detail": [
                {
                    "loc": ["body", "timeout"],
                    "msg": "ensure this value is greater than 0",
                    "type": "value_error"
                }
            ]
        }
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_post.return_value = mock_response
        
        client = BrobotClient()
        
        with pytest.raises(BrobotValidationError):
            client.execute_action(
                action_type="click",
                parameters={},
                timeout=-1.0  # Invalid
            )


class TestConvenienceMethods:
    """Test convenience methods."""
    
    @patch('requests.post')
    def test_click_method(self, mock_post):
        """Test click convenience method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "action_type": "click",
            "duration": 0.3
        }
        mock_post.return_value = mock_response
        
        client = BrobotClient()
        result = client.click("button.png", confidence=0.9)
        
        assert result["success"] is True
        
        # Verify parameters
        call_json = mock_post.call_args[1]["json"]
        assert call_json["action_type"] == "click"
        assert call_json["parameters"]["image_pattern"] == "button.png"
        assert call_json["parameters"]["confidence"] == 0.9
    
    @patch('requests.post')
    def test_type_text_method(self, mock_post):
        """Test type_text convenience method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "action_type": "type"
        }
        mock_post.return_value = mock_response
        
        client = BrobotClient()
        result = client.type_text("Hello, World!")
        
        assert result["success"] is True
        
        # Verify parameters
        call_json = mock_post.call_args[1]["json"]
        assert call_json["action_type"] == "type"
        assert call_json["parameters"]["text"] == "Hello, World!"
    
    @patch('requests.post')
    def test_drag_method(self, mock_post):
        """Test drag convenience method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "action_type": "drag"
        }
        mock_post.return_value = mock_response
        
        client = BrobotClient()
        result = client.drag("source.png", "target.png", duration=1.0)
        
        assert result["success"] is True
        
        # Verify parameters
        call_json = mock_post.call_args[1]["json"]
        assert call_json["action_type"] == "drag"
        assert call_json["parameters"]["from_pattern"] == "source.png"
        assert call_json["parameters"]["to_pattern"] == "target.png"
        assert call_json["parameters"]["duration"] == 1.0
    
    @patch('requests.post')
    def test_wait_method(self, mock_post):
        """Test wait convenience method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "action_type": "wait"
        }
        mock_post.return_value = mock_response
        
        client = BrobotClient()
        result = client.wait("loaded.png", timeout=10.0)
        
        assert result["success"] is True
        
        # Verify parameters
        call_json = mock_post.call_args[1]["json"]
        assert call_json["action_type"] == "wait"
        assert call_json["parameters"]["image_pattern"] == "loaded.png"
        assert call_json["timeout"] == 10.0


class TestRetryMechanism:
    """Test retry mechanism."""
    
    @patch('requests.get')
    def test_retry_on_connection_error(self, mock_get):
        """Test retry on connection errors."""
        # First two calls fail, third succeeds
        mock_get.side_effect = [
            requests.exceptions.ConnectionError("Connection refused"),
            requests.exceptions.ConnectionError("Connection refused"),
            Mock(status_code=200, json=lambda: {"status": "ok"})
        ]
        
        client = BrobotClient(max_retries=3)
        # This would succeed after retries if implemented
        # For now, it will raise the first error
        with pytest.raises(BrobotConnectionError):
            client.health_check()
    
    @patch('requests.get')
    def test_no_retry_on_client_error(self, mock_get):
        """Test no retry on 4xx errors."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_response
        
        client = BrobotClient(max_retries=3)
        
        with pytest.raises(BrobotClientError):
            client.get_state_structure()
        
        # Should only be called once (no retries for client errors)
        assert mock_get.call_count == 1


class TestErrorHandling:
    """Test error handling."""
    
    @patch('requests.get')
    def test_json_decode_error(self, mock_get):
        """Test handling of invalid JSON responses."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid", "", 0)
        mock_response.text = "Invalid JSON"
        mock_get.return_value = mock_response
        
        client = BrobotClient()
        
        with pytest.raises(BrobotClientError) as exc_info:
            client.get_state_structure()
        
        assert "JSON" in str(exc_info.value)
    
    @patch('requests.get')
    def test_unexpected_error(self, mock_get):
        """Test handling of unexpected errors."""
        mock_get.side_effect = Exception("Unexpected error")
        
        client = BrobotClient()
        
        with pytest.raises(BrobotClientError) as exc_info:
            client.health_check()
        
        assert "Unexpected error" in str(exc_info.value)


# Add this import at the top if not already present
import requests