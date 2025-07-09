# Brobot CLI

Command-line interface wrapper for Brobot automation framework, designed to work with the MCP server.

## Overview

This CLI provides JSON-based commands to interact with Brobot's automation engine:
- `get-state-structure` - Retrieve the application state model
- `get-observation` - Get current screen observation with active states
- `execute-action` - Execute automation actions (click, type, drag, etc.)

## Building

Prerequisites:
- Java 11 or higher
- Gradle 7.6 or higher
- Brobot framework

Build the CLI JAR:
```bash
gradle shadowJar
# or
./gradlew shadowJar
```

The JAR will be created at `build/libs/brobot-cli.jar`

## Usage

### Get State Structure
```bash
java -jar brobot-cli.jar get-state-structure
java -jar brobot-cli.jar get-state-structure --pretty
```

### Get Observation
```bash
java -jar brobot-cli.jar get-observation
java -jar brobot-cli.jar get-observation --pretty --screenshot
```

### Execute Action
```bash
# Click action
java -jar brobot-cli.jar execute-action '{"actionType":"click","parameters":{"image_pattern":"button.png"}}'

# Type action
java -jar brobot-cli.jar execute-action '{"actionType":"type","parameters":{"text":"Hello World"}}'

# Drag action
java -jar brobot-cli.jar execute-action '{"actionType":"drag","parameters":{"start_x":100,"start_y":100,"end_x":500,"end_y":500}}'
```

## Integration with MCP Server

The Python MCP server uses this CLI via subprocess calls:
```python
subprocess.run(["java", "-jar", "brobot-cli.jar", "get-observation"], capture_output=True)
```

## Current Status

This is currently a mock implementation for testing the MCP server integration. 
TODO items for full Brobot integration:
- Replace mock data with actual Brobot state management
- Implement real screenshot capture using Brobot
- Connect to Brobot's action execution engine
- Add configuration for target application