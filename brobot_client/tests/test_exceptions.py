"""Unit tests for client exceptions."""

import pytest
from brobot_client.exceptions import (
    BrobotClientError,
    BrobotConnectionError,
    BrobotTimeoutError,
    BrobotValidationError
)


class TestExceptionHierarchy:
    """Test exception class hierarchy."""
    
    def test_base_exception(self):
        """Test base BrobotClientError."""
        error = BrobotClientError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)
    
    def test_connection_error(self):
        """Test BrobotConnectionError."""
        error = BrobotConnectionError("Connection failed")
        assert str(error) == "Connection failed"
        assert isinstance(error, BrobotClientError)
        assert isinstance(error, Exception)
    
    def test_timeout_error(self):
        """Test BrobotTimeoutError."""
        error = BrobotTimeoutError("Request timed out")
        assert str(error) == "Request timed out"
        assert isinstance(error, BrobotClientError)
        assert isinstance(error, Exception)
    
    def test_validation_error(self):
        """Test BrobotValidationError."""
        error = BrobotValidationError("Invalid parameter")
        assert str(error) == "Invalid parameter"
        assert isinstance(error, BrobotClientError)
        assert isinstance(error, Exception)


class TestExceptionUsage:
    """Test exception usage patterns."""
    
    def test_raising_base_error(self):
        """Test raising base error."""
        with pytest.raises(BrobotClientError) as exc_info:
            raise BrobotClientError("General error")
        
        assert "General error" in str(exc_info.value)
    
    def test_catching_specific_errors(self):
        """Test catching specific error types."""
        # Test catching connection error specifically
        try:
            raise BrobotConnectionError("Network issue")
        except BrobotConnectionError as e:
            assert "Network issue" in str(e)
        except BrobotClientError:
            pytest.fail("Should catch BrobotConnectionError specifically")
    
    def test_catching_base_error(self):
        """Test catching base error catches all subtypes."""
        errors = [
            BrobotConnectionError("Connection error"),
            BrobotTimeoutError("Timeout error"),
            BrobotValidationError("Validation error")
        ]
        
        for error in errors:
            try:
                raise error
            except BrobotClientError as e:
                assert str(error) == str(e)
            except Exception:
                pytest.fail(f"Should catch {type(error).__name__} as BrobotClientError")


class TestExceptionMessages:
    """Test exception message formatting."""
    
    def test_simple_message(self):
        """Test simple error message."""
        error = BrobotClientError("Simple message")
        assert str(error) == "Simple message"
    
    def test_formatted_message(self):
        """Test formatted error message."""
        url = "http://localhost:8000"
        error = BrobotConnectionError(f"Failed to connect to {url}")
        assert str(error) == f"Failed to connect to {url}"
    
    def test_multiline_message(self):
        """Test multiline error message."""
        message = """Failed to execute action:
        - Action type: click
        - Pattern: button.png
        - Error: Pattern not found"""
        
        error = BrobotClientError(message)
        assert str(error) == message
    
    def test_empty_message(self):
        """Test empty error message."""
        error = BrobotClientError("")
        assert str(error) == ""
    
    def test_none_message(self):
        """Test None as error message."""
        # Should handle None gracefully
        error = BrobotClientError(None)
        assert str(error) == "None"


class TestExceptionChaining:
    """Test exception chaining and cause."""
    
    def test_exception_chaining(self):
        """Test exception chaining with __cause__."""
        original_error = ValueError("Original error")
        
        try:
            raise original_error
        except ValueError as e:
            try:
                raise BrobotClientError("Wrapped error") from e
            except BrobotClientError as wrapped:
                assert wrapped.__cause__ is original_error
                assert str(wrapped) == "Wrapped error"
                assert str(wrapped.__cause__) == "Original error"
    
    def test_exception_context(self):
        """Test exception context preservation."""
        try:
            try:
                raise ConnectionError("Network error")
            except ConnectionError:
                raise BrobotConnectionError("Failed to connect to server")
        except BrobotConnectionError as e:
            assert e.__context__ is not None
            assert isinstance(e.__context__, ConnectionError)
            assert str(e.__context__) == "Network error"


class TestExceptionAttributes:
    """Test custom exception attributes."""
    
    def test_custom_attributes(self):
        """Test adding custom attributes to exceptions."""
        error = BrobotClientError("Test error")
        error.status_code = 500
        error.request_url = "http://localhost:8000/api/v1/test"
        
        assert hasattr(error, 'status_code')
        assert error.status_code == 500
        assert hasattr(error, 'request_url')
        assert error.request_url == "http://localhost:8000/api/v1/test"
    
    def test_validation_error_details(self):
        """Test validation error with details."""
        error = BrobotValidationError("Validation failed")
        error.validation_errors = [
            {"field": "timeout", "message": "Must be positive"},
            {"field": "action_type", "message": "Unknown action"}
        ]
        
        assert hasattr(error, 'validation_errors')
        assert len(error.validation_errors) == 2
        assert error.validation_errors[0]["field"] == "timeout"