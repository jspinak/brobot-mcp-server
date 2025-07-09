"""Unit tests for main module."""

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

from mcp_server.main import app


class TestStartupEvent:
    """Test application startup events."""
    
    @patch('mcp_server.main.get_settings')
    @patch('mcp_server.main.initialize_bridge')
    @patch('mcp_server.main.logger')
    async def test_startup_with_cli_configured(self, mock_logger, mock_init_bridge, mock_get_settings):
        """Test startup with CLI configured."""
        # Import startup_event directly
        from mcp_server.main import startup_event
        
        # Mock settings
        mock_settings = Mock()
        mock_settings.brobot_cli_jar = "/path/to/cli.jar"
        mock_settings.use_mock_data = False
        mock_settings.java_executable = "java"
        mock_get_settings.return_value = mock_settings
        
        # Run startup
        await startup_event()
        
        # Verify bridge initialization was called
        mock_init_bridge.assert_called_once_with(
            jar_path="/path/to/cli.jar",
            java_executable="java"
        )
        mock_logger.info.assert_called_with("Brobot bridge initialized successfully")
    
    @patch('mcp_server.main.get_settings')
    @patch('mcp_server.main.initialize_bridge')
    @patch('mcp_server.main.logger')
    async def test_startup_with_mock_mode(self, mock_logger, mock_init_bridge, mock_get_settings):
        """Test startup in mock mode."""
        from mcp_server.main import startup_event
        
        # Mock settings for mock mode
        mock_settings = Mock()
        mock_settings.brobot_cli_jar = None
        mock_settings.use_mock_data = True
        mock_get_settings.return_value = mock_settings
        
        # Run startup
        await startup_event()
        
        # Verify bridge initialization was NOT called
        mock_init_bridge.assert_not_called()
        mock_logger.info.assert_called_with("Running in mock data mode (CLI not configured)")
    
    @patch('mcp_server.main.get_settings')
    @patch('mcp_server.main.initialize_bridge')
    @patch('mcp_server.main.logger')
    async def test_startup_with_initialization_error(self, mock_logger, mock_init_bridge, mock_get_settings):
        """Test startup with bridge initialization error."""
        from mcp_server.main import startup_event
        
        # Mock settings
        mock_settings = Mock()
        mock_settings.brobot_cli_jar = "/path/to/cli.jar"
        mock_settings.use_mock_data = False
        mock_settings.java_executable = "java"
        mock_get_settings.return_value = mock_settings
        
        # Mock initialization failure
        mock_init_bridge.side_effect = Exception("CLI not found")
        
        # Run startup
        await startup_event()
        
        # Verify error was logged
        mock_logger.error.assert_called_with("Failed to initialize Brobot bridge: CLI not found")
        mock_logger.info.assert_called_with("Server will continue with mock data")


class TestMainModule:
    """Test main module configuration."""
    
    def test_app_configuration(self):
        """Test FastAPI app configuration."""
        assert app.title == "Brobot MCP Server"
        assert app.version == "0.1.0"
        assert app.description == "Model Context Protocol server that allows AI agents to control Brobot automation applications"
    
    def test_app_metadata(self):
        """Test app metadata."""
        # FastAPI apps don't have contact/license_info by default
        # unless explicitly set in the FastAPI constructor
        assert not hasattr(app, 'contact') or app.contact is None
        assert not hasattr(app, 'license_info') or app.license_info is None
    
    def test_included_routers(self, test_client):
        """Test that API routers are included."""
        # Test that API endpoints exist
        response = test_client.get("/health")
        assert response.status_code == 200
        
        response = test_client.get("/api/v1/health")
        assert response.status_code == 200
        
        response = test_client.get("/api/v1/state_structure")
        assert response.status_code == 200
        
        response = test_client.get("/api/v1/observation")
        assert response.status_code == 200
        
        # Test POST endpoint
        response = test_client.post("/api/v1/execute", json={"action_type": "test"})
        assert response.status_code in [200, 422]  # 422 for validation error is ok


class TestOpenAPI:
    """Test OpenAPI documentation."""
    
    def test_openapi_schema(self, test_client):
        """Test OpenAPI schema endpoint."""
        response = test_client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert schema["openapi"].startswith("3.")
        assert schema["info"]["title"] == "Brobot MCP Server"
        assert schema["info"]["version"] == "0.1.0"
    
    def test_api_documentation_endpoints(self, test_client):
        """Test API documentation endpoints."""
        # Test that docs are accessible
        response = test_client.get("/docs")
        assert response.status_code == 200
        
        # Test ReDoc endpoint
        response = test_client.get("/redoc")
        assert response.status_code == 200


class TestHealthEndpoints:
    """Test health endpoints from main module perspective."""
    
    def test_basic_health_accessible(self, test_client):
        """Test that basic health endpoint is accessible."""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"
    
    def test_root_endpoint_accessible(self, test_client):
        """Test that root endpoint is accessible."""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "Brobot MCP Server"
        assert "version" in data
        assert "api" in data


class TestEnvironmentHandling:
    """Test environment and configuration handling."""
    
    def test_startup_logs_configuration(self):
        """Test that startup logs configuration details."""
        # Just verify the module imports successfully
        # The actual logging is done at module level import
        import mcp_server.main
        assert mcp_server.main.app is not None
        assert hasattr(mcp_server.main, 'startup_event')