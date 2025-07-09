# Brobot MCP Server API Documentation

## Overview

The Brobot MCP Server provides a RESTful API that follows the Model Context Protocol (MCP) specification. This API allows AI agents to interact with GUI applications through the Brobot automation framework.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. This may change in future versions.

## API Versioning

The API uses URL versioning. Current version: `v1`

All API endpoints are prefixed with `/api/v1/`

## Endpoints

### 1. Get State Structure

Retrieve the complete state structure of the application, including all states and their transitions.

**Endpoint:** `GET /api/v1/state_structure`

**Response:**
```json
{
  "states": [
    {
      "name": "main_menu",
      "description": "Application main menu",
      "images": ["main_menu_logo.png", "main_menu_title.png"],
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
    "application": "Sample Application",
    "version": "1.0.0"
  }
}
```

### 2. Get Current Observation

Get the current state of the application including active states and screenshot.

**Endpoint:** `GET /api/v1/observation`

**Response:**
```json
{
  "timestamp": "2024-01-20T10:30:00Z",
  "active_states": [
    {
      "name": "main_menu",
      "confidence": 0.95,
      "matched_patterns": ["main_menu_logo.png"]
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

### 3. Execute Action

Execute an automation action on the application.

**Endpoint:** `POST /api/v1/execute`

**Request Body:**
```json
{
  "action_type": "click",
  "parameters": {
    "image_pattern": "button_submit.png",
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
    "pattern_found": true
  }
}
```

## Action Types

### Click
Click on an image pattern or specific location.

**Parameters:**
- `image_pattern` (string): Image file to search for
- `confidence` (float): Minimum confidence score (0.0-1.0)
- `location` (object): Alternative to image_pattern, specify {x, y}

### Type
Type text at the current cursor location.

**Parameters:**
- `text` (string): Text to type
- `typing_speed` (int): Characters per minute (optional)

### Drag
Drag from one location to another.

**Parameters:**
- `start_x`, `start_y` (int): Starting coordinates
- `end_x`, `end_y` (int): Ending coordinates
- `duration` (float): Drag duration in seconds

### Wait
Wait for a specific state or condition.

**Parameters:**
- `state_name` (string): State to wait for
- `timeout` (float): Maximum wait time in seconds

## Error Handling

The API uses standard HTTP status codes:

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Endpoint not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

Error responses include a detail message:

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Rate Limiting

Currently, there are no rate limits. This may change in production deployments.

## Webhooks

Future versions will support webhooks for state change notifications.

## Example Usage

### Python
```python
import requests

# Get current observation
response = requests.get("http://localhost:8000/api/v1/observation")
observation = response.json()

# Execute a click action
action = {
    "action_type": "click",
    "parameters": {"image_pattern": "button.png"},
    "timeout": 5.0
}
response = requests.post("http://localhost:8000/api/v1/execute", json=action)
result = response.json()
```

### cURL
```bash
# Get state structure
curl http://localhost:8000/api/v1/state_structure

# Execute action
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{"action_type":"click","parameters":{"image_pattern":"button.png"}}'
```

## Interactive Documentation

The server provides interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

These interfaces allow you to explore and test the API directly from your browser.