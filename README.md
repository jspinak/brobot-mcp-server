# Brobot MCP Server

A Model Context Protocol (MCP) server that enables AI agents to control and interact with Brobot automation applications.

## Overview

The Brobot MCP Server provides a bridge between AI agents and the Brobot Java automation framework. It exposes Brobot's GUI automation capabilities through a RESTful API, allowing AI systems to:

- Query the current state structure of an application
- Observe the current state with screenshots and active state information
- Execute automation actions (click, type, drag, etc.)

## Architecture

The server acts as a middleware layer:

```
AI Agent <--> Python MCP Server <--> Java Brobot CLI <--> Target Application
```

## Key Features

- **State Management**: Query and understand the application's state structure
- **Real-time Observation**: Get screenshots and active state information
- **Action Execution**: Perform GUI automation actions through the API
- **FastAPI-based**: Modern, fast, and well-documented API
- **Type Safety**: Full Pydantic model validation
- **Developer-friendly**: Automatic API documentation at `/docs`

## Installation

### Prerequisites

- Python 3.8 or higher
- Java 11 or higher (for Brobot CLI)
- Brobot framework

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/brobot-mcp-server.git
cd brobot-mcp-server
```

2. Install the package:
```bash
pip install -e .
```

3. For development, install with dev dependencies:
```bash
pip install -e .[dev]
```

## Usage

### Starting the Server

Run the server using:

```bash
python -m mcp_server.main
```

Or use the installed command:

```bash
brobot-mcp-server
```

The server will start on `http://localhost:8000` by default.

### API Documentation

Once the server is running, visit:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### Health Check

Verify the server is running:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok"}
```

## CLI Integration

The server can operate in two modes:

### 1. Mock Mode (Default)
Uses hardcoded mock data for testing and development.

### 2. CLI Mode
Integrates with the Brobot Java CLI for real automation control.

#### Setting up CLI Mode:

1. Build the Brobot CLI:
```bash
cd brobot-cli
gradle shadowJar  # or ./gradlew shadowJar
```

2. Configure the server:
Create a `.env` file:
```env
USE_MOCK_DATA=false
BROBOT_CLI_JAR=brobot-cli/build/libs/brobot-cli.jar
```

3. Start the server:
```bash
python -m mcp_server.main
```

The server will automatically detect and use the CLI when available.

## API Endpoints

### Core Endpoints

- `GET /api/v1/state_structure` - Get the application's state model
- `GET /api/v1/observation` - Get current observation with screenshot
- `POST /api/v1/execute` - Execute an automation action
- `GET /api/v1/health` - Extended health check with CLI status

## Python Client Library

A Python client library is available for easy integration:

```bash
pip install brobot-client
```

Quick example:
```python
from brobot_client import BrobotClient

with BrobotClient() as client:
    # Get current state
    observation = client.get_observation()
    
    # Perform actions
    client.click("button.png")
    client.type_text("Hello, Brobot!")
```

See the [client documentation](brobot_client/README.md) for full details.

## Development

### Running Tests

```bash
pytest
```

### Code Quality

Run linting and formatting:

```bash
black mcp_server tests
flake8 mcp_server tests
mypy mcp_server
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Roadmap

### Milestone 1: Core Server & API Contract Definition ✅
- [x] Initial project setup with FastAPI
- [x] Mock API endpoints implementation

### Milestone 2: Brobot Integration ✅
- [x] Create Brobot Java CLI wrapper
- [x] Wire API endpoints to live Brobot CLI

### Milestone 3: Developer Experience
- [x] Python client library
- [ ] Comprehensive documentation

### Milestone 4: Quality & Automation
- [ ] Unit and integration tests
- [ ] CI/CD pipeline

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and feature requests, please use the [GitHub issue tracker](https://github.com/yourusername/brobot-mcp-server/issues).