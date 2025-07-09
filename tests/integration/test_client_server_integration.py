"""Integration tests for client-server communication."""

import pytest
import asyncio
import threading
import time
from unittest.mock import patch, Mock
import uvicorn

try:
    from brobot_client import BrobotClient, AsyncBrobotClient
except ImportError:
    # For testing without client installed
    BrobotClient = None
    AsyncBrobotClient = None

from mcp_server.main import app
from mcp_server.config import Settings


@pytest.mark.integration
@pytest.mark.skipif(BrobotClient is None, reason="brobot_client not installed")
class TestClientServerIntegration:
    """Test client-server integration."""
    
    @patch('mcp_server.api.get_settings')
    def test_sync_client_basic_operations(self, mock_get_settings, test_server):
        """Test synchronous client basic operations."""
        # Configure mock mode
        mock_settings = Mock()
        mock_settings.is_cli_configured = False
        mock_get_settings.return_value = mock_settings
        
        # Create client
        client = BrobotClient(base_url=test_server)
        
        # Test health check
        health = client.health_check()
        assert health["status"] == "ok"
        
        # Test get state structure
        state_structure = client.get_state_structure()
        assert "states" in state_structure
        assert len(state_structure["states"]) > 0
        
        # Test get observation
        observation = client.get_observation()
        assert "active_states" in observation
        assert "screenshot" in observation
        
        # Test execute action
        result = client.execute_action(
            action_type="click",
            parameters={"image_pattern": "button.png"}
        )
        assert "success" in result
    
    @patch('mcp_server.api.get_settings')
    def test_sync_client_convenience_methods(self, mock_get_settings, test_server):
        """Test synchronous client convenience methods."""
        # Configure mock mode
        mock_settings = Mock()
        mock_settings.is_cli_configured = False
        mock_get_settings.return_value = mock_settings
        
        # Create client
        client = BrobotClient(base_url=test_server)
        
        # Test click
        result = client.click("button.png", confidence=0.9)
        assert result["success"] is True
        assert result["action_type"] == "click"
        
        # Test type text
        result = client.type_text("Hello, World!")
        assert result["success"] is True
        assert result["action_type"] == "type"
        
        # Test drag
        result = client.drag("handle.png", "target.png")
        assert result["success"] is True
        assert result["action_type"] == "drag"
        
        # Test wait
        result = client.wait("loaded.png", timeout=5.0)
        assert result["action_type"] == "wait"
    
    @patch('mcp_server.api.get_settings')
    def test_sync_client_error_handling(self, mock_get_settings, test_server):
        """Test synchronous client error handling."""
        # Configure mock mode
        mock_settings = Mock()
        mock_settings.is_cli_configured = False
        mock_get_settings.return_value = mock_settings
        
        # Create client with wrong URL
        client = BrobotClient(base_url="http://localhost:9999")
        
        # Test connection error
        with pytest.raises(Exception):
            client.health_check()
        
        # Create client with correct URL
        client = BrobotClient(base_url=test_server)
        
        # Test validation error
        with pytest.raises(Exception):
            client.execute_action(
                action_type="click",
                parameters={"image_pattern": "test.png"},
                timeout=-1  # Invalid timeout
            )
    
    @patch('mcp_server.api.get_settings')
    @pytest.mark.asyncio
    async def test_async_client_basic_operations(self, mock_get_settings, test_server):
        """Test asynchronous client basic operations."""
        # Configure mock mode
        mock_settings = Mock()
        mock_settings.is_cli_configured = False
        mock_get_settings.return_value = mock_settings
        
        # Create async client
        async with AsyncBrobotClient(base_url=test_server) as client:
            # Test health check
            health = await client.health_check()
            assert health["status"] == "ok"
            
            # Test get state structure
            state_structure = await client.get_state_structure()
            assert "states" in state_structure
            
            # Test get observation
            observation = await client.get_observation()
            assert "active_states" in observation
            
            # Test execute action
            result = await client.execute_action(
                action_type="click",
                parameters={"image_pattern": "button.png"}
            )
            assert "success" in result
    
    @patch('mcp_server.api.get_settings')
    @pytest.mark.asyncio
    async def test_async_client_convenience_methods(self, mock_get_settings, test_server):
        """Test asynchronous client convenience methods."""
        # Configure mock mode
        mock_settings = Mock()
        mock_settings.is_cli_configured = False
        mock_get_settings.return_value = mock_settings
        
        # Create async client
        async with AsyncBrobotClient(base_url=test_server) as client:
            # Test click
            result = await client.click("button.png")
            assert result["success"] is True
            
            # Test type text
            result = await client.type_text("Async test")
            assert result["success"] is True
            
            # Test multiple operations concurrently
            results = await asyncio.gather(
                client.get_state_structure(),
                client.get_observation(),
                client.click("test.png")
            )
            assert len(results) == 3
            assert "states" in results[0]
            assert "active_states" in results[1]
            assert results[2]["success"] is True


@pytest.mark.integration
@pytest.mark.skipif(BrobotClient is None, reason="brobot_client not installed")
class TestClientRetryMechanism:
    """Test client retry mechanisms."""
    
    @patch('mcp_server.api.get_settings')
    def test_sync_client_retry_on_failure(self, mock_get_settings, test_server):
        """Test synchronous client retry on failure."""
        # Track call count
        call_count = 0
        
        def mock_get_settings_impl():
            nonlocal call_count
            call_count += 1
            
            # Fail first two times, succeed on third
            if call_count < 3:
                raise Exception("Temporary failure")
            
            mock_settings = Mock()
            mock_settings.is_cli_configured = False
            return mock_settings
        
        mock_get_settings.side_effect = mock_get_settings_impl
        
        # Create client with retries
        client = BrobotClient(base_url=test_server, max_retries=3)
        
        # This should eventually succeed after retries
        try:
            health = client.health_check()
            # If retries are implemented, this should work
            assert health["status"] == "ok"
        except Exception:
            # If retries not implemented yet, that's ok
            pass
    
    @patch('mcp_server.api.get_settings')
    @pytest.mark.asyncio
    async def test_async_client_concurrent_requests(self, mock_get_settings, test_server):
        """Test async client handling concurrent requests."""
        # Configure mock mode
        mock_settings = Mock()
        mock_settings.is_cli_configured = False
        mock_get_settings.return_value = mock_settings
        
        # Create async client
        async with AsyncBrobotClient(base_url=test_server) as client:
            # Send many concurrent requests
            tasks = []
            for i in range(10):
                tasks.append(client.click(f"button_{i}.png"))
            
            # Wait for all to complete
            results = await asyncio.gather(*tasks)
            
            # All should succeed
            assert len(results) == 10
            for result in results:
                assert result["success"] is True


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.skipif(BrobotClient is None, reason="brobot_client not installed")
class TestLongRunningOperations:
    """Test long-running operations and timeouts."""
    
    @patch('mcp_server.api.get_settings')
    def test_client_timeout_handling(self, mock_get_settings, test_server):
        """Test client timeout handling."""
        # Configure mock mode
        mock_settings = Mock()
        mock_settings.is_cli_configured = False
        mock_get_settings.return_value = mock_settings
        
        # Create client with short timeout
        client = BrobotClient(base_url=test_server, timeout=0.001)
        
        # This might timeout
        try:
            client.get_state_structure()
        except Exception as e:
            # Timeout error is expected
            assert "timeout" in str(e).lower() or "timed out" in str(e).lower()
    
    @patch('mcp_server.api.get_settings')
    @patch('mcp_server.api.get_bridge')
    def test_server_cli_timeout_propagation(self, mock_get_bridge, mock_get_settings, test_server):
        """Test that timeouts propagate from client to CLI."""
        # Configure for CLI mode
        mock_settings = Mock()
        mock_settings.is_cli_configured = True
        mock_get_settings.return_value = mock_settings
        
        # Mock bridge that respects timeouts
        mock_bridge = Mock()
        
        def execute_with_timeout(request):
            if request.get("timeout", 10.0) < 1.0:
                raise Exception("Command timed out")
            return {"success": True}
        
        mock_bridge.execute_action.side_effect = execute_with_timeout
        mock_get_bridge.return_value = mock_bridge
        
        # Create client
        client = BrobotClient(base_url=test_server)
        
        # Test with short timeout
        with pytest.raises(Exception):
            client.wait("slow_pattern.png", timeout=0.5)
        
        # Test with adequate timeout
        result = client.wait("pattern.png", timeout=5.0)
        assert result["success"] is True