# Brobot MCP Server Tests

This directory contains all tests for the Brobot MCP Server project.

## Test Structure

```
tests/
├── unit/                   # Unit tests for individual components
│   ├── test_api.py        # Tests for API endpoints
│   ├── test_brobot_bridge.py  # Tests for Java CLI bridge
│   ├── test_config.py     # Tests for configuration
│   ├── test_main.py       # Tests for main application
│   └── test_models.py     # Tests for Pydantic models
├── integration/           # Integration tests
│   ├── test_server_cli_integration.py  # Server-CLI communication
│   └── test_client_server_integration.py  # Client-Server communication
├── conftest.py           # Shared pytest fixtures
├── utils.py              # Test utilities and helpers
├── factories.py          # Mock factories for testing
└── README.md            # This file
```

## Running Tests

### Run all tests with coverage:
```bash
# From project root
./scripts/run_tests.sh
```

### Run specific test categories:
```bash
# Unit tests only
pytest tests/unit -v

# Integration tests only
pytest tests/integration -v

# Tests with specific markers
pytest -m unit
pytest -m integration
pytest -m "not slow"
```

### Run with coverage:
```bash
pytest --cov=mcp_server --cov-report=html --cov-report=term-missing
```

### Run tests for client library:
```bash
cd brobot_client
pytest --cov=brobot_client --cov-report=html
```

## Test Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.cli` - Tests requiring Java CLI
- `@pytest.mark.mock` - Tests using mock data
- `@pytest.mark.asyncio` - Async tests

## Test Utilities

### MockDataGenerator
Generates realistic mock data for testing:
```python
from tests.utils import MockDataGenerator

# Generate mock state structure
state_structure = MockDataGenerator.generate_state_structure()

# Generate mock observation
observation = MockDataGenerator.generate_observation()

# Generate mock action result
result = MockDataGenerator.generate_action_result(success=True)
```

### Test Factories
Create complex mock objects:
```python
from tests.factories import SettingsFactory, BridgeFactory

# Create settings
settings = SettingsFactory.create(use_mock_data=True)

# Create mock bridge
bridge = BridgeFactory.create_mock_bridge(available=True)
```

### API Test Helpers
Validate API responses:
```python
from tests.utils import APITestHelper

# Validate state structure
APITestHelper.assert_valid_state_structure(response_data)

# Validate observation
APITestHelper.assert_valid_observation(response_data)
```

## Writing New Tests

### Unit Test Template
```python
import pytest
from unittest.mock import Mock, patch

class TestMyComponent:
    """Test MyComponent functionality."""
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        # Arrange
        component = MyComponent()
        
        # Act
        result = component.do_something()
        
        # Assert
        assert result == expected_value
    
    @patch('module.external_dependency')
    def test_with_mock(self, mock_dep):
        """Test with mocked dependency."""
        mock_dep.return_value = "mocked"
        
        result = MyComponent().use_dependency()
        
        assert result == "mocked"
```

### Integration Test Template
```python
@pytest.mark.integration
class TestIntegration:
    """Test component integration."""
    
    def test_end_to_end_workflow(self, test_server):
        """Test complete workflow."""
        # Setup
        client = BrobotClient(base_url=test_server)
        
        # Execute workflow
        state = client.get_state_structure()
        observation = client.get_observation()
        result = client.execute_action("click", {"image": "button.png"})
        
        # Verify
        assert result["success"] is True
```

## Coverage Reports

After running tests with coverage, reports are available at:
- Server coverage: `coverage/html/index.html`
- Client coverage: `coverage/client_html/index.html`
- XML report: `coverage/coverage.xml`

## Continuous Integration

Tests are automatically run on:
- Push to main branch
- Pull requests
- Tagged releases

See `.github/workflows/test.yml` for CI configuration.

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure you're running from project root with proper PYTHONPATH
2. **Missing dependencies**: Install test dependencies with `pip install -e ".[test]"`
3. **Java CLI tests failing**: These require the Java CLI to be built. They're marked with `@pytest.mark.cli`
4. **Async test warnings**: Use `@pytest.mark.asyncio` for async tests

### Debug Mode

Run tests with verbose output and no capture:
```bash
pytest -vv -s tests/unit/test_api.py::TestHealthEndpoints::test_basic_health_endpoint
```

### Test Isolation

Each test should be independent. Use fixtures for setup/teardown:
```python
@pytest.fixture
def clean_environment(tmp_path, monkeypatch):
    """Provide clean test environment."""
    monkeypatch.chdir(tmp_path)
    yield tmp_path
    # Cleanup happens automatically
```