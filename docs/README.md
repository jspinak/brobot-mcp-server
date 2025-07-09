# Brobot MCP Server - Comprehensive Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation Guide](#installation-guide)
4. [Configuration](#configuration)
5. [API Reference](#api-reference)
6. [Python Client Library](#python-client-library)
7. [Integration Examples](#integration-examples)
8. [Development](#development)
9. [Troubleshooting](#troubleshooting)
10. [Contributing](#contributing)

## Overview

The Brobot Model Context Protocol (MCP) Server enables AI agents to control GUI applications through the Brobot automation framework. It provides a RESTful API that bridges the gap between AI systems and desktop automation.

### Key Benefits

- **AI-Driven Automation**: Enable LLMs and AI agents to interact with desktop applications
- **State-Based Control**: Leverage Brobot's state management for reliable automation
- **Visual Verification**: Get screenshots and visual feedback for AI decision-making
- **Language Agnostic**: RESTful API accessible from any programming language
- **Real-time Observation**: Monitor application state changes in real-time

### Use Cases

- **Automated Testing**: AI agents can perform exploratory testing
- **Task Automation**: Natural language commands translated to GUI actions
- **Process Mining**: Observe and document user workflows
- **Accessibility**: Voice-controlled desktop automation
- **RPA Integration**: Combine with existing RPA workflows

## Architecture

### System Components

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │     │                 │
│   AI Agent      │────▶│  Python MCP     │────▶│  Java Brobot    │────▶│    Target       │
│  (GPT, Claude)  │◀────│    Server       │◀────│      CLI        │◀────│  Application    │
│                 │     │                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
      HTTP/REST              Subprocess               JVM                    GUI Events
```

### Data Flow

1. **AI Agent** sends HTTP requests with automation commands
2. **MCP Server** validates requests and translates to CLI commands
3. **Brobot CLI** executes actions using the Brobot framework
4. **Target Application** receives GUI events (clicks, typing, etc.)
5. **Response** flows back with results, screenshots, and state info

### Technology Stack

- **Server**: Python 3.8+, FastAPI, Pydantic
- **CLI Bridge**: Java 11+, Brobot Framework, picocli
- **Client Libraries**: Python (requests/aiohttp)
- **Protocols**: HTTP/REST, JSON

## Installation Guide

### System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: 3.8 or higher
- **Java**: JDK 11 or higher
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Display**: Required for GUI automation

### Step 1: Install Python Dependencies

```bash
# Clone the repository
git clone https://github.com/jspinak/brobot-mcp-server.git
cd brobot-mcp-server

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the server
pip install -e .

# Install development dependencies (optional)
pip install -e .[dev]
```

### Step 2: Build the Brobot CLI

```bash
# Navigate to CLI directory
cd brobot-cli

# Build with Gradle
./gradlew shadowJar  # On Windows: gradlew.bat shadowJar

# Verify the JAR was created
ls build/libs/brobot-cli.jar
```

### Step 3: Configure the Server

Create a `.env` file in the project root:

```env
# Server Configuration
MCP_HOST=0.0.0.0
MCP_PORT=8000
MCP_LOG_LEVEL=info

# Brobot CLI Configuration
BROBOT_CLI_JAR=brobot-cli/build/libs/brobot-cli.jar
USE_MOCK_DATA=false

# Optional: Custom Java path
# JAVA_EXECUTABLE=/usr/bin/java
```

### Step 4: Start the Server

```bash
# Start in development mode
python -m mcp_server.main

# Or use uvicorn directly
uvicorn mcp_server.main:app --reload

# For production
uvicorn mcp_server.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_HOST` | Server bind address | `0.0.0.0` |
| `MCP_PORT` | Server port | `8000` |
| `MCP_LOG_LEVEL` | Logging level (debug/info/warn/error) | `info` |
| `BROBOT_CLI_JAR` | Path to Brobot CLI JAR | Auto-detected |
| `JAVA_EXECUTABLE` | Java executable path | `java` |
| `CLI_TIMEOUT` | CLI command timeout (seconds) | `30.0` |
| `USE_MOCK_DATA` | Use mock data instead of real CLI | `true` |

### Brobot Configuration

The Brobot CLI uses its own configuration for:
- Image pattern directories
- Screenshot settings
- Action timing parameters

Place Brobot configuration in `brobot-cli/src/main/resources/`.

## API Reference

### Base URL

```
http://localhost:8000/api/v1
```

### Authentication

Currently, no authentication is required. Future versions will support API keys.

### Endpoints

#### GET /health

Check server and Brobot CLI status.

**Response:**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "brobot_connected": true,
  "timestamp": "2024-01-20T10:30:00Z"
}
```

#### GET /state_structure

Retrieve the complete state structure of the application.

**Response:**
```json
{
  "states": [
    {
      "name": "main_menu",
      "description": "Application main menu",
      "images": ["main_menu_logo.png", "menu_button.png"],
      "transitions": [
        {
          "from_state": "main_menu",
          "to_state": "login_screen",
          "action": "click_login",
          "probability": 0.95
        }
      ],
      "is_initial": true,
      "is_final": false
    }
  ],
  "current_state": "main_menu",
  "metadata": {
    "application": "MyApp",
    "version": "1.0.0"
  }
}
```

#### GET /observation

Get current observation including screenshot and active states.

**Response:**
```json
{
  "timestamp": "2024-01-20T10:30:00Z",
  "active_states": [
    {
      "name": "dashboard",
      "confidence": 0.95,
      "matched_patterns": ["dashboard_header.png", "user_menu.png"]
    }
  ],
  "screenshot": "base64_encoded_image_data...",
  "screen_width": 1920,
  "screen_height": 1080,
  "metadata": {
    "capture_duration": 0.125,
    "analysis_duration": 0.087
  }
}
```

#### POST /execute

Execute an automation action.

**Request:**
```json
{
  "action_type": "click",
  "parameters": {
    "image_pattern": "submit_button.png",
    "confidence": 0.9
  },
  "target_state": "form_submitted",
  "timeout": 5.0
}
```

**Response:**
```json
{
  "success": true,
  "action_type": "click",
  "duration": 0.523,
  "result_state": "form_submitted",
  "error": null,
  "metadata": {
    "click_location": {"x": 640, "y": 480},
    "pattern_found": true,
    "confidence": 0.92
  }
}
```

### Action Types

#### click
Click on an image pattern or location.

**Parameters:**
- `image_pattern` (string): Image file to search for
- `location` (object): `{x: number, y: number}` coordinates
- `confidence` (float): Minimum match confidence (0.0-1.0)

#### type
Type text at current cursor location.

**Parameters:**
- `text` (string): Text to type
- `typing_speed` (int): Characters per minute

#### drag
Drag between two points.

**Parameters:**
- `start_x`, `start_y` (int): Starting coordinates
- `end_x`, `end_y` (int): Ending coordinates
- `duration` (float): Drag duration in seconds

#### wait
Wait for a specific state.

**Parameters:**
- `state_name` (string): State to wait for
- `timeout` (float): Maximum wait time

### Error Responses

```json
{
  "detail": "Error message describing what went wrong"
}
```

HTTP Status Codes:
- `200 OK`: Success
- `400 Bad Request`: Invalid parameters
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server or CLI error

## Python Client Library

### Installation

```bash
pip install brobot-client
```

### Quick Start

```python
from brobot_client import BrobotClient

# Create client
client = BrobotClient(base_url="http://localhost:8000")

# Get current state
observation = client.get_observation()
print(f"Active state: {observation.get_most_confident_state().name}")

# Perform actions
client.click("login_button.png")
client.type_text("username@example.com")
client.click("submit.png")

# Wait for result
client.wait_for_state("dashboard", timeout=30)
```

### Async Usage

```python
import asyncio
from brobot_client import AsyncBrobotClient

async def automate_login():
    async with AsyncBrobotClient() as client:
        await client.click("login_button.png")
        await client.type_text("username")
        await client.click("submit.png")

asyncio.run(automate_login())
```

## Integration Examples

### OpenAI GPT Integration

```python
import openai
from brobot_client import BrobotClient

def execute_natural_language_command(command: str):
    # Use GPT to parse the command
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Convert user commands to Brobot actions."},
            {"role": "user", "content": command}
        ]
    )
    
    # Execute the actions
    with BrobotClient() as client:
        # ... execute based on GPT response
```

### Anthropic Claude Integration

```python
from anthropic import Anthropic
from brobot_client import BrobotClient

client = BrobotClient()
anthropic = Anthropic()

# Get current screen state
observation = client.get_observation()

# Ask Claude what to do
response = anthropic.messages.create(
    model="claude-3",
    messages=[{
        "role": "user",
        "content": f"Current screen shows: {observation.active_states}. How should I proceed?"
    }]
)

# Execute Claude's suggestions
# ...
```

### LangChain Integration

```python
from langchain.tools import Tool
from brobot_client import BrobotClient

# Create Brobot tool for LangChain
def create_brobot_tools():
    client = BrobotClient()
    
    return [
        Tool(
            name="click_screen",
            func=lambda pattern: client.click(pattern),
            description="Click on a UI element by image pattern"
        ),
        Tool(
            name="type_text",
            func=lambda text: client.type_text(text),
            description="Type text into the current field"
        ),
        Tool(
            name="observe_screen",
            func=lambda: client.get_observation(),
            description="Get current screen state and screenshot"
        )
    ]
```

## Development

### Project Structure

```
brobot-mcp-server/
├── mcp_server/          # Python server implementation
│   ├── main.py         # FastAPI application
│   ├── api.py          # API endpoints
│   ├── models.py       # Pydantic models
│   ├── brobot_bridge.py # CLI subprocess management
│   └── config.py       # Configuration management
├── brobot-cli/         # Java CLI wrapper
│   └── src/main/java/  # Java source code
├── brobot_client/      # Python client library
│   └── brobot_client/  # Client implementation
├── tests/              # Test suites
├── docs/               # Documentation
└── examples/           # Usage examples
```

### Running Tests

```bash
# Python tests
pytest tests/

# Java tests
cd brobot-cli
./gradlew test

# Integration tests
python test_cli_integration.py
```

### Code Style

- Python: Black formatter, flake8 linter
- Java: Google Java Style Guide
- API: RESTful conventions

## Troubleshooting

### Common Issues

#### Server won't start
- Check Python version: `python --version` (needs 3.8+)
- Verify dependencies: `pip list`
- Check port availability: `lsof -i :8000`

#### CLI not found
- Verify JAR exists: `ls brobot-cli/build/libs/`
- Check Java version: `java -version` (needs 11+)
- Set BROBOT_CLI_JAR environment variable

#### Actions fail
- Ensure target application is visible
- Check image patterns exist and are valid
- Verify Brobot configuration
- Review logs for detailed errors

#### Connection errors
- Confirm server is running: `curl http://localhost:8000/health`
- Check firewall settings
- Verify network connectivity

### Debug Mode

Enable detailed logging:

```bash
MCP_LOG_LEVEL=debug python -m mcp_server.main
```

### Performance Tuning

- Increase CLI timeout for slow systems
- Use specific image regions to speed up pattern matching
- Cache frequently used patterns
- Run server with multiple workers in production

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## Support

- GitHub Issues: https://github.com/jspinak/brobot-mcp-server/issues
- Documentation: https://brobot.dev/docs/integrations/mcp-server
- Community Discord: https://discord.gg/brobot