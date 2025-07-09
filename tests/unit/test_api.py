"""Unit tests for API endpoints."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json
import base64

from fastapi.testclient import TestClient
from mcp_server.main import app
from mcp_server.models import StateStructure, Observation, ActionResult
from mcp_server.brobot_bridge import BrobotCLIError


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_basic_health_endpoint(self, test_client):
        """Test basic /health endpoint."""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    
    @patch('mcp_server.api.get_settings')
    @patch('mcp_server.api.get_bridge')
    def test_extended_health_endpoint_with_cli(self, mock_get_bridge, mock_get_settings, test_client):
        """Test extended health endpoint with CLI connected."""
        # Mock settings
        mock_settings = Mock()
        mock_settings.brobot_cli_jar = "/path/to/cli.jar"
        mock_settings.use_mock_data = False
        mock_get_settings.return_value = mock_settings
        
        # Mock bridge
        mock_bridge = Mock()
        mock_bridge.is_available.return_value = True
        mock_get_bridge.return_value = mock_bridge
        
        response = test_client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "0.1.0"
        assert data["brobot_connected"] is True
        assert "timestamp" in data
    
    @patch('mcp_server.api.get_settings')
    def test_extended_health_endpoint_mock_mode(self, mock_get_settings, test_client):
        """Test extended health endpoint in mock mode."""
        # Mock settings for mock mode
        mock_settings = Mock()
        mock_settings.brobot_cli_jar = None
        mock_settings.use_mock_data = True
        mock_get_settings.return_value = mock_settings
        
        response = test_client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["brobot_connected"] is False


class TestRootEndpoint:
    """Test root endpoint."""
    
    def test_root_endpoint(self, test_client):
        """Test root endpoint returns API information."""
        response = test_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Brobot MCP Server"
        assert data["version"] == "0.1.0"
        assert "api" in data
        assert data["api"]["state_structure"] == "/api/v1/state_structure"
        assert data["api"]["observation"] == "/api/v1/observation"
        assert data["api"]["execute"] == "/api/v1/execute"


class TestStateStructureEndpoint:
    """Test state structure endpoint."""
    
    @patch('mcp_server.api.get_settings')
    def test_state_structure_mock_mode(self, mock_get_settings, test_client):
        """Test state structure endpoint in mock mode."""
        # Configure for mock mode
        mock_settings = Mock()
        mock_settings.is_cli_configured = False
        mock_get_settings.return_value = mock_settings
        
        response = test_client.get("/api/v1/state_structure")
        
        assert response.status_code == 200
        data = response.json()
        assert "states" in data
        assert len(data["states"]) > 0
        assert data["states"][0]["name"] == "main_menu"
        assert "current_state" in data
        assert "metadata" in data
    
    @patch('mcp_server.api.get_settings')
    @patch('mcp_server.api.get_bridge')
    def test_state_structure_cli_mode(self, mock_get_bridge, mock_get_settings, test_client):
        """Test state structure endpoint with CLI integration."""
        # Configure for CLI mode
        mock_settings = Mock()
        mock_settings.is_cli_configured = True
        mock_get_settings.return_value = mock_settings
        
        # Mock bridge response
        mock_bridge = Mock()
        mock_bridge.get_state_structure.return_value = {
            "states": [
                {
                    "name": "test_state",
                    "description": "Test",
                    "images": ["test.png"],
                    "transitions": [
                        {
                            "fromState": "test_state",
                            "toState": "next_state",
                            "action": "click",
                            "probability": 0.9
                        }
                    ],
                    "isInitial": True,
                    "isFinal": False
                }
            ],
            "currentState": "test_state",
            "metadata": {"source": "cli"}
        }
        mock_get_bridge.return_value = mock_bridge
        
        response = test_client.get("/api/v1/state_structure")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["states"]) == 1
        assert data["states"][0]["name"] == "test_state"
        assert data["metadata"]["source"] == "cli"
    
    @patch('mcp_server.api.get_settings')
    @patch('mcp_server.api.get_bridge')
    def test_state_structure_cli_error(self, mock_get_bridge, mock_get_settings, test_client):
        """Test state structure endpoint with CLI error."""
        # Configure for CLI mode
        mock_settings = Mock()
        mock_settings.is_cli_configured = True
        mock_get_settings.return_value = mock_settings
        
        # Mock bridge error
        mock_bridge = Mock()
        mock_bridge.get_state_structure.side_effect = BrobotCLIError("CLI failed")
        mock_get_bridge.return_value = mock_bridge
        
        response = test_client.get("/api/v1/state_structure")
        
        assert response.status_code == 500
        assert "CLI failed" in response.json()["detail"]


class TestObservationEndpoint:
    """Test observation endpoint."""
    
    @patch('mcp_server.api.get_settings')
    def test_observation_mock_mode(self, mock_get_settings, test_client):
        """Test observation endpoint in mock mode."""
        # Configure for mock mode
        mock_settings = Mock()
        mock_settings.is_cli_configured = False
        mock_get_settings.return_value = mock_settings
        
        response = test_client.get("/api/v1/observation")
        
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert "active_states" in data
        assert len(data["active_states"]) > 0
        assert "screenshot" in data
        assert "screen_width" in data
        assert data["screen_width"] == 1920
        assert "metadata" in data
    
    @patch('mcp_server.api.get_settings')
    @patch('mcp_server.api.get_bridge')
    def test_observation_cli_mode(self, mock_get_bridge, mock_get_settings, test_client):
        """Test observation endpoint with CLI integration."""
        # Configure for CLI mode
        mock_settings = Mock()
        mock_settings.is_cli_configured = True
        mock_get_settings.return_value = mock_settings
        
        # Mock bridge response
        mock_bridge = Mock()
        mock_bridge.get_observation.return_value = {
            "timestamp": "2024-01-20T10:30:00",
            "activeStates": [
                {
                    "name": "dashboard",
                    "confidence": 0.85,
                    "matchedPatterns": ["dashboard.png"]
                }
            ],
            "screenshot": "base64imagedata",
            "screenWidth": 1920,
            "screenHeight": 1080,
            "metadata": {"source": "cli"}
        }
        mock_get_bridge.return_value = mock_bridge
        
        response = test_client.get("/api/v1/observation")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["active_states"]) == 1
        assert data["active_states"][0]["name"] == "dashboard"
        assert data["active_states"][0]["confidence"] == 0.85
        assert data["screenshot"] == "base64imagedata"
    
    @patch('mcp_server.api.get_settings')
    @patch('mcp_server.api.get_bridge')
    def test_observation_cli_error(self, mock_get_bridge, mock_get_settings, test_client):
        """Test observation endpoint with CLI error."""
        # Configure for CLI mode
        mock_settings = Mock()
        mock_settings.is_cli_configured = True
        mock_get_settings.return_value = mock_settings
        
        # Mock bridge error
        mock_bridge = Mock()
        mock_bridge.get_observation.side_effect = Exception("Unexpected error")
        mock_get_bridge.return_value = mock_bridge
        
        response = test_client.get("/api/v1/observation")
        
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]


class TestExecuteEndpoint:
    """Test execute action endpoint."""
    
    @patch('mcp_server.api.get_settings')
    def test_execute_click_mock_mode(self, mock_get_settings, test_client):
        """Test execute click action in mock mode."""
        # Configure for mock mode
        mock_settings = Mock()
        mock_settings.is_cli_configured = False
        mock_get_settings.return_value = mock_settings
        
        request_data = {
            "action_type": "click",
            "parameters": {
                "image_pattern": "button.png",
                "confidence": 0.9
            },
            "target_state": "next_screen",
            "timeout": 5.0
        }
        
        response = test_client.post("/api/v1/execute", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["action_type"] == "click"
        assert "duration" in data
        assert "metadata" in data
        assert data["metadata"]["pattern_found"] is True
    
    @patch('mcp_server.api.get_settings')
    def test_execute_type_mock_mode(self, mock_get_settings, test_client):
        """Test execute type action in mock mode."""
        # Configure for mock mode
        mock_settings = Mock()
        mock_settings.is_cli_configured = False
        mock_get_settings.return_value = mock_settings
        
        request_data = {
            "action_type": "type",
            "parameters": {
                "text": "Hello, World!"
            }
        }
        
        response = test_client.post("/api/v1/execute", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["action_type"] == "type"
        assert data["metadata"]["text_entered"] == "Hello, World!"
    
    @patch('mcp_server.api.get_settings')
    def test_execute_unknown_action_mock_mode(self, mock_get_settings, test_client):
        """Test execute unknown action in mock mode."""
        # Configure for mock mode
        mock_settings = Mock()
        mock_settings.is_cli_configured = False
        mock_get_settings.return_value = mock_settings
        
        request_data = {
            "action_type": "unknown_action",
            "parameters": {}
        }
        
        response = test_client.post("/api/v1/execute", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "Unknown action type: unknown_action"
    
    @patch('mcp_server.api.get_settings')
    @patch('mcp_server.api.get_bridge')
    def test_execute_cli_mode(self, mock_get_bridge, mock_get_settings, test_client):
        """Test execute action with CLI integration."""
        # Configure for CLI mode
        mock_settings = Mock()
        mock_settings.is_cli_configured = True
        mock_get_settings.return_value = mock_settings
        
        # Mock bridge response
        mock_bridge = Mock()
        mock_bridge.execute_action.return_value = {
            "success": True,
            "actionType": "click",
            "duration": 0.456,
            "resultState": "dashboard",
            "error": None,
            "metadata": {"source": "cli"}
        }
        mock_get_bridge.return_value = mock_bridge
        
        request_data = {
            "action_type": "click",
            "parameters": {"image_pattern": "login.png"},
            "timeout": 10.0
        }
        
        response = test_client.post("/api/v1/execute", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["duration"] == 0.456
        assert data["result_state"] == "dashboard"
        
        # Verify bridge was called correctly
        mock_bridge.execute_action.assert_called_once()
        call_args = mock_bridge.execute_action.call_args[0][0]
        assert call_args["actionType"] == "click"
        assert call_args["parameters"]["image_pattern"] == "login.png"
        assert call_args["timeout"] == 10.0
    
    @patch('mcp_server.api.get_settings')
    @patch('mcp_server.api.get_bridge')
    def test_execute_cli_error(self, mock_get_bridge, mock_get_settings, test_client):
        """Test execute action with CLI error."""
        # Configure for CLI mode
        mock_settings = Mock()
        mock_settings.is_cli_configured = True
        mock_get_settings.return_value = mock_settings
        
        # Mock bridge error
        mock_bridge = Mock()
        mock_bridge.execute_action.side_effect = BrobotCLIError("Pattern not found")
        mock_get_bridge.return_value = mock_bridge
        
        request_data = {
            "action_type": "click",
            "parameters": {"image_pattern": "nonexistent.png"}
        }
        
        response = test_client.post("/api/v1/execute", json=request_data)
        
        assert response.status_code == 200  # Still 200, but success=false
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "Pattern not found"
    
    def test_execute_invalid_request(self, test_client):
        """Test execute with invalid request data."""
        # Missing required field
        request_data = {
            "parameters": {}
        }
        
        response = test_client.post("/api/v1/execute", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_execute_invalid_timeout(self, test_client):
        """Test execute with invalid timeout."""
        request_data = {
            "action_type": "wait",
            "parameters": {},
            "timeout": -5.0  # Invalid negative timeout
        }
        
        response = test_client.post("/api/v1/execute", json=request_data)
        
        assert response.status_code == 422  # Validation error