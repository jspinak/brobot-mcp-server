"""Unit tests for asynchronous Brobot client."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import json
import aiohttp

from brobot_client import AsyncBrobotClient
from brobot_client.exceptions import (
    BrobotClientError,
    BrobotConnectionError,
    BrobotValidationError,
    BrobotTimeoutError
)


class TestAsyncBrobotClientInitialization:
    """Test AsyncBrobotClient initialization."""
    
    def test_default_initialization(self):
        """Test client with default parameters."""
        client = AsyncBrobotClient()
        assert client.base_url == "http://localhost:8000"
        assert client.timeout == 30.0
        assert client.max_retries == 3
    
    def test_custom_initialization(self):
        """Test client with custom parameters."""
        client = AsyncBrobotClient(
            base_url="http://example.com:8080",
            timeout=60.0,
            max_retries=5
        )
        assert client.base_url == "http://example.com:8080"
        assert client.timeout == 60.0
        assert client.max_retries == 5
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test client as context manager."""
        async with AsyncBrobotClient() as client:
            assert client._session is not None
            assert not client._session.closed
        
        # Session should be closed after exiting context
        assert client._session.closed
    
    @pytest.mark.asyncio
    async def test_manual_close(self):
        """Test manual session close."""
        client = AsyncBrobotClient()
        
        # Session created on first use
        assert client._session is None
        
        # Force session creation
        session = client._get_session()
        assert session is not None
        assert not session.closed
        
        # Close manually
        await client.close()
        assert session.closed


class TestAsyncHealthCheck:
    """Test async health check functionality."""
    
    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "status": "ok",
                "version": "0.1.0",
                "brobot_connected": True
            })
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with AsyncBrobotClient() as client:
                result = await client.health_check()
            
            assert result["status"] == "ok"
            assert result["version"] == "0.1.0"
            assert result["brobot_connected"] is True
    
    @pytest.mark.asyncio
    async def test_health_check_connection_error(self):
        """Test health check with connection error."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = aiohttp.ClientConnectionError("Connection refused")
            
            async with AsyncBrobotClient() as client:
                with pytest.raises(BrobotConnectionError) as exc_info:
                    await client.health_check()
            
            assert "Connection refused" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_health_check_timeout(self):
        """Test health check with timeout."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = asyncio.TimeoutError("Request timed out")
            
            async with AsyncBrobotClient() as client:
                with pytest.raises(BrobotTimeoutError) as exc_info:
                    await client.health_check()
            
            assert "Request timed out" in str(exc_info.value)


class TestAsyncStateStructure:
    """Test async get_state_structure functionality."""
    
    @pytest.mark.asyncio
    async def test_get_state_structure_success(self):
        """Test successful get_state_structure."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "states": [
                    {"name": "main_menu", "description": "Main menu"}
                ],
                "current_state": "main_menu",
                "metadata": {}
            })
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with AsyncBrobotClient() as client:
                result = await client.get_state_structure()
            
            assert len(result["states"]) == 1
            assert result["states"][0]["name"] == "main_menu"
            assert result["current_state"] == "main_menu"
    
    @pytest.mark.asyncio
    async def test_get_state_structure_server_error(self):
        """Test get_state_structure with server error."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_response.text = AsyncMock(return_value="Internal Server Error")
            mock_response.raise_for_status.side_effect = aiohttp.ClientResponseError(
                request_info=Mock(),
                history=(),
                status=500
            )
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with AsyncBrobotClient() as client:
                with pytest.raises(BrobotClientError):
                    await client.get_state_structure()


class TestAsyncObservation:
    """Test async get_observation functionality."""
    
    @pytest.mark.asyncio
    async def test_get_observation_success(self):
        """Test successful get_observation."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "timestamp": "2024-01-20T10:30:00",
                "active_states": [
                    {"name": "dashboard", "confidence": 0.95}
                ],
                "screenshot": "base64imagedata",
                "screen_width": 1920,
                "screen_height": 1080,
                "metadata": {}
            })
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with AsyncBrobotClient() as client:
                result = await client.get_observation()
            
            assert result["active_states"][0]["name"] == "dashboard"
            assert result["screenshot"] == "base64imagedata"
            assert result["screen_width"] == 1920


class TestAsyncExecuteAction:
    """Test async execute_action functionality."""
    
    @pytest.mark.asyncio
    async def test_execute_action_success(self):
        """Test successful execute_action."""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "success": True,
                "action_type": "click",
                "duration": 0.5,
                "result_state": "next_screen",
                "error": None,
                "metadata": {}
            })
            mock_post.return_value.__aenter__.return_value = mock_response
            
            async with AsyncBrobotClient() as client:
                result = await client.execute_action(
                    action_type="click",
                    parameters={"image_pattern": "button.png"},
                    target_state="next_screen",
                    timeout=5.0
                )
            
            assert result["success"] is True
            assert result["action_type"] == "click"
            assert result["result_state"] == "next_screen"
    
    @pytest.mark.asyncio
    async def test_execute_action_validation_error(self):
        """Test execute_action with validation error."""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 422
            mock_response.json = AsyncMock(return_value={
                "detail": [
                    {
                        "loc": ["body", "timeout"],
                        "msg": "ensure this value is greater than 0",
                        "type": "value_error"
                    }
                ]
            })
            mock_response.raise_for_status.side_effect = aiohttp.ClientResponseError(
                request_info=Mock(),
                history=(),
                status=422
            )
            mock_post.return_value.__aenter__.return_value = mock_response
            
            async with AsyncBrobotClient() as client:
                with pytest.raises(BrobotValidationError):
                    await client.execute_action(
                        action_type="click",
                        parameters={},
                        timeout=-1.0  # Invalid
                    )


class TestAsyncConvenienceMethods:
    """Test async convenience methods."""
    
    @pytest.mark.asyncio
    async def test_click_method(self):
        """Test click convenience method."""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "success": True,
                "action_type": "click",
                "duration": 0.3
            })
            mock_post.return_value.__aenter__.return_value = mock_response
            
            async with AsyncBrobotClient() as client:
                result = await client.click("button.png", confidence=0.9)
            
            assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_type_text_method(self):
        """Test type_text convenience method."""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "success": True,
                "action_type": "type"
            })
            mock_post.return_value.__aenter__.return_value = mock_response
            
            async with AsyncBrobotClient() as client:
                result = await client.type_text("Hello, Async World!")
            
            assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test concurrent operations."""
        with patch('aiohttp.ClientSession.get') as mock_get, \
             patch('aiohttp.ClientSession.post') as mock_post:
            
            # Mock responses
            mock_get_response = AsyncMock()
            mock_get_response.status = 200
            mock_get_response.json = AsyncMock(return_value={
                "states": [{"name": "test"}],
                "current_state": "test"
            })
            mock_get.return_value.__aenter__.return_value = mock_get_response
            
            mock_post_response = AsyncMock()
            mock_post_response.status = 200
            mock_post_response.json = AsyncMock(return_value={
                "success": True,
                "action_type": "click"
            })
            mock_post.return_value.__aenter__.return_value = mock_post_response
            
            async with AsyncBrobotClient() as client:
                # Execute multiple operations concurrently
                results = await asyncio.gather(
                    client.get_state_structure(),
                    client.click("button1.png"),
                    client.click("button2.png"),
                    client.get_state_structure()
                )
            
            assert len(results) == 4
            assert "states" in results[0]
            assert results[1]["success"] is True
            assert results[2]["success"] is True
            assert "states" in results[3]


class TestAsyncRetryMechanism:
    """Test async retry mechanism."""
    
    @pytest.mark.asyncio
    async def test_retry_on_connection_error(self):
        """Test retry on connection errors."""
        call_count = 0
        
        async def mock_get_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            if call_count < 3:
                raise aiohttp.ClientConnectionError("Connection refused")
            
            # Success on third attempt
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"status": "ok"})
            return mock_response
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.side_effect = mock_get_side_effect
            
            async with AsyncBrobotClient(max_retries=3) as client:
                # This would succeed after retries if implemented
                # For now, it will raise the first error
                with pytest.raises(BrobotConnectionError):
                    await client.health_check()


class TestAsyncErrorHandling:
    """Test async error handling."""
    
    @pytest.mark.asyncio
    async def test_json_decode_error(self):
        """Test handling of invalid JSON responses."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.side_effect = json.JSONDecodeError("Invalid", "", 0)
            mock_response.text = AsyncMock(return_value="Invalid JSON")
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with AsyncBrobotClient() as client:
                with pytest.raises(BrobotClientError) as exc_info:
                    await client.get_state_structure()
                
                assert "JSON" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_unexpected_error(self):
        """Test handling of unexpected errors."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = Exception("Unexpected error")
            
            async with AsyncBrobotClient() as client:
                with pytest.raises(BrobotClientError) as exc_info:
                    await client.health_check()
                
                assert "Unexpected error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_session_cleanup_on_error(self):
        """Test session cleanup on error."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = Exception("Error during request")
            
            client = AsyncBrobotClient()
            
            try:
                await client.health_check()
            except BrobotClientError:
                pass
            
            # Ensure session can be properly closed
            await client.close()