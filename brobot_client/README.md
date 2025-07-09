# Brobot MCP Client Library

A Python client library for interacting with the Brobot MCP Server, providing both synchronous and asynchronous interfaces.

## Installation

```bash
pip install brobot-client
```

Or install from source:
```bash
cd brobot_client
pip install -e .
```

## Quick Start

### Synchronous Client

```python
from brobot_client import BrobotClient

# Create client instance
client = BrobotClient(base_url="http://localhost:8000")

# Get current observation
observation = client.get_observation()
print(f"Active states: {[s.name for s in observation.active_states]}")

# Click on an element
result = client.click(image_pattern="submit_button.png")
print(f"Click successful: {result.success}")

# Type text
client.type_text("Hello, Brobot!")

# Close the client
client.close()
```

### Using Context Manager

```python
from brobot_client import BrobotClient

with BrobotClient() as client:
    # Get state structure
    state_structure = client.get_state_structure()
    
    # Perform actions
    client.click("login_button.png")
    client.type_text("username")
```

### Asynchronous Client

```python
import asyncio
from brobot_client import AsyncBrobotClient

async def main():
    async with AsyncBrobotClient() as client:
        # Get observation
        observation = await client.get_observation()
        
        # Execute actions concurrently
        await asyncio.gather(
            client.click("button1.png"),
            client.get_state_structure()
        )

asyncio.run(main())
```

## Core Features

### State Management

```python
# Get the application state structure
state_structure = client.get_state_structure()

# Explore states
for state in state_structure.states:
    print(f"State: {state.name}")
    print(f"  Description: {state.description}")
    print(f"  Initial: {state.is_initial}")
    print(f"  Transitions:")
    for transition in state.transitions:
        print(f"    -> {transition.to_state} via {transition.action}")
```

### Observations

```python
# Get current observation
observation = client.get_observation()

# Get most confident state
top_state = observation.get_most_confident_state()
if top_state:
    print(f"Most likely state: {top_state.name} ({top_state.confidence:.2%})")

# Save screenshot
if observation.screenshot:
    observation.save_screenshot("current_screen.png")
```

### Actions

#### Click Actions

```python
from brobot_client import Location

# Click on image pattern
client.click(image_pattern="button.png", confidence=0.9)

# Click at specific location
client.click(location=Location(x=500, y=300))

# Click with custom timeout
client.click("slow_loading_button.png", timeout=30.0)
```

#### Typing Actions

```python
# Type text
client.type_text("Hello, World!")

# Type with custom speed (chars per minute)
client.type_text("Slow typing...", typing_speed=120)
```

#### Drag Actions

```python
# Drag between locations
start = Location(x=100, y=100)
end = Location(x=500, y=500)
client.drag(start, end, duration=2.0)

# Drag between image patterns
client.drag("drag_handle.png", "drop_zone.png")

# Mixed drag (pattern to location)
client.drag("item.png", Location(x=800, y=400))
```

#### Wait Actions

```python
# Wait for specific state
client.wait_for_state("dashboard", timeout=30.0)
```

### Error Handling

```python
from brobot_client import (
    BrobotConnectionError,
    BrobotTimeoutError,
    BrobotActionError
)

try:
    client.click("button.png")
except BrobotConnectionError as e:
    print(f"Connection failed: {e}")
except BrobotTimeoutError as e:
    print(f"Request timed out: {e}")
except BrobotActionError as e:
    print(f"Action failed: {e}")
    print(f"Action type: {e.action_type}")
    print(f"Error details: {e.error_details}")
```

### Retry Logic

```python
from brobot_client import BrobotClient
from brobot_client.retry import retry

# Create client with automatic retries
client = BrobotClient(base_url="http://localhost:8000")

# Use retry decorator for custom retry logic
@retry(max_attempts=5, base_delay=2.0)
def click_with_retry():
    return client.click("unreliable_button.png")

result = click_with_retry()
```

## Advanced Usage

### Custom Request Timeout

```python
# Set default timeout for all requests
client = BrobotClient(timeout=60.0)

# Override timeout for specific request
client.execute_action("complex_action", timeout=120.0)
```

### Working with Regions

```python
from brobot_client import Region

# Define a screen region
search_area = Region(x=100, y=100, width=800, height=600)

# Get region center
center = search_area.center  # Location(x=500, y=400)

# Use in actions (when API supports it)
params = {"search_region": search_area.to_dict()}
client.execute_action("click", parameters=params)
```

### Custom Actions

```python
# Execute custom actions not covered by convenience methods
result = client.execute_action(
    action_type="scroll",
    parameters={
        "direction": "down",
        "amount": 500
    },
    target_state="scrolled_view"
)
```

### Health Checks

```python
# Check server health
health = client.get_health()
print(f"Server status: {health['status']}")
print(f"Brobot connected: {health['brobot_connected']}")
```

## Async Examples

### Concurrent Operations

```python
async def perform_login(client, username, password):
    # Click login button
    await client.click("login_button.png")
    
    # Enter credentials
    await client.click("username_field.png")
    await client.type_text(username)
    
    await client.click("password_field.png")
    await client.type_text(password)
    
    # Submit
    await client.click("submit_button.png")
    
    # Wait for dashboard
    await client.wait_for_state("dashboard")

async def main():
    async with AsyncBrobotClient() as client:
        await perform_login(client, "user@example.com", "password123")
```

### Parallel Observations

```python
async def monitor_states(client, duration=60):
    """Monitor state changes for a duration."""
    import time
    
    start_time = time.time()
    observations = []
    
    while time.time() - start_time < duration:
        obs = await client.get_observation()
        observations.append(obs)
        await asyncio.sleep(1.0)
    
    return observations
```

## Configuration

### Environment Variables

The client respects these environment variables:

- `BROBOT_MCP_URL`: Default server URL
- `BROBOT_MCP_TIMEOUT`: Default timeout in seconds
- `BROBOT_MCP_VERIFY_SSL`: Whether to verify SSL certificates

```python
import os

# Set via environment
os.environ["BROBOT_MCP_URL"] = "https://my-server.com"
os.environ["BROBOT_MCP_TIMEOUT"] = "45"

# Client will use these defaults
client = BrobotClient()  # Uses https://my-server.com with 45s timeout
```

## Debugging

Enable debug logging to see detailed information:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Now client operations will log details
client = BrobotClient()
client.click("button.png")  # Logs request/response details
```

## Best Practices

1. **Use Context Managers**: Always use `with` statements to ensure proper cleanup
2. **Handle Errors**: Wrap actions in try-except blocks for production code
3. **Set Appropriate Timeouts**: Adjust timeouts based on your application's responsiveness
4. **Reuse Client Instances**: Create one client and reuse it for multiple operations
5. **Use Async for Concurrent Operations**: Use AsyncBrobotClient when you need parallelism

## API Reference

See the [API documentation](https://github.com/jspinak/brobot-mcp-server/docs/client-api.md) for complete details on all classes and methods.

## Contributing

Contributions are welcome! Please see the [contributing guide](../CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.