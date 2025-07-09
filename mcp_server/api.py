"""API endpoints for the MCP server."""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import base64
import logging
from typing import Dict, Any

from .models import (
    StateStructure, State, StateTransition,
    Observation, ActiveState,
    ActionRequest, ActionResult,
    HealthStatus
)
from .config import get_settings
from .brobot_bridge import get_bridge, BrobotCLIError

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/v1", tags=["MCP"])


# Mock data generators
def get_mock_state_structure() -> StateStructure:
    """Generate mock state structure data."""
    return StateStructure(
        states=[
            State(
                name="main_menu",
                description="Application main menu",
                images=["main_menu_logo.png", "main_menu_title.png"],
                transitions=[
                    StateTransition(
                        from_state="main_menu",
                        to_state="login_screen",
                        action="click_login",
                        probability=0.95
                    ),
                    StateTransition(
                        from_state="main_menu",
                        to_state="settings",
                        action="click_settings",
                        probability=0.95
                    )
                ],
                is_initial=True,
                is_final=False
            ),
            State(
                name="login_screen",
                description="User login screen",
                images=["login_form.png", "username_field.png", "password_field.png"],
                transitions=[
                    StateTransition(
                        from_state="login_screen",
                        to_state="dashboard",
                        action="submit_login",
                        probability=0.90
                    ),
                    StateTransition(
                        from_state="login_screen",
                        to_state="main_menu",
                        action="click_back",
                        probability=0.95
                    )
                ],
                is_initial=False,
                is_final=False
            ),
            State(
                name="dashboard",
                description="User dashboard",
                images=["dashboard_header.png", "user_profile.png"],
                transitions=[
                    StateTransition(
                        from_state="dashboard",
                        to_state="main_menu",
                        action="logout",
                        probability=0.95
                    )
                ],
                is_initial=False,
                is_final=False
            ),
            State(
                name="settings",
                description="Application settings",
                images=["settings_header.png", "settings_menu.png"],
                transitions=[
                    StateTransition(
                        from_state="settings",
                        to_state="main_menu",
                        action="click_back",
                        probability=0.95
                    )
                ],
                is_initial=False,
                is_final=False
            )
        ],
        current_state="main_menu",
        metadata={
            "application": "Sample Application",
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat()
        }
    )


def get_mock_observation() -> Observation:
    """Generate mock observation data."""
    # Create a simple 1x1 pixel transparent PNG as mock screenshot
    mock_screenshot_bytes = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    )
    mock_screenshot_base64 = base64.b64encode(mock_screenshot_bytes).decode('utf-8')
    
    return Observation(
        timestamp=datetime.now(),
        active_states=[
            ActiveState(
                name="main_menu",
                confidence=0.95,
                matched_patterns=["main_menu_logo.png", "main_menu_title.png"]
            ),
            ActiveState(
                name="login_screen",
                confidence=0.15,
                matched_patterns=[]
            )
        ],
        screenshot=mock_screenshot_base64,
        screen_width=1920,
        screen_height=1080,
        metadata={
            "capture_duration": 0.125,
            "analysis_duration": 0.087,
            "total_patterns_checked": 12
        }
    )


def get_mock_action_result(request: ActionRequest) -> ActionResult:
    """Generate mock action result."""
    # Simulate different results based on action type
    if request.action_type == "click":
        return ActionResult(
            success=True,
            action_type=request.action_type,
            duration=0.523,
            result_state=request.target_state or "unknown",
            error=None,
            metadata={
                "click_location": {"x": 640, "y": 480},
                "pattern_found": True,
                "confidence": 0.92
            }
        )
    elif request.action_type == "type":
        return ActionResult(
            success=True,
            action_type=request.action_type,
            duration=1.234,
            result_state=request.target_state,
            error=None,
            metadata={
                "text_entered": request.parameters.get("text", ""),
                "typing_speed": 50  # chars per minute
            }
        )
    elif request.action_type == "drag":
        return ActionResult(
            success=True,
            action_type=request.action_type,
            duration=0.876,
            result_state=request.target_state,
            error=None,
            metadata={
                "start_location": {"x": 100, "y": 100},
                "end_location": {"x": 500, "y": 500},
                "drag_duration": 0.5
            }
        )
    else:
        return ActionResult(
            success=False,
            action_type=request.action_type,
            duration=0.001,
            result_state=None,
            error=f"Unknown action type: {request.action_type}",
            metadata={}
        )


# API Endpoints
@router.get("/state_structure", response_model=StateStructure, summary="Get application state structure")
async def get_state_structure() -> StateStructure:
    """
    Retrieve the complete state structure of the application.
    
    This endpoint returns the state graph including all states,
    their transitions, and associated image patterns.
    """
    settings = get_settings()
    
    # Use CLI if configured, otherwise fall back to mock data
    if settings.is_cli_configured:
        try:
            bridge = get_bridge()
            cli_response = bridge.get_state_structure()
            
            # Convert CLI response to our Pydantic model
            return StateStructure(
                states=[
                    State(
                        name=s["name"],
                        description=s.get("description", ""),
                        images=s.get("images", []),
                        transitions=[
                            StateTransition(
                                from_state=t["fromState"],
                                to_state=t["toState"],
                                action=t["action"],
                                probability=t.get("probability", 0.0)
                            )
                            for t in s.get("transitions", [])
                        ],
                        is_initial=s.get("isInitial", False),
                        is_final=s.get("isFinal", False)
                    )
                    for s in cli_response.get("states", [])
                ],
                current_state=cli_response.get("currentState"),
                metadata=cli_response.get("metadata", {})
            )
        except BrobotCLIError as e:
            logger.error(f"CLI error getting state structure: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error getting state structure: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    # Fall back to mock data
    logger.info("Using mock state structure data")
    return get_mock_state_structure()


@router.get("/observation", response_model=Observation, summary="Get current observation")
async def get_observation() -> Observation:
    """
    Get the current observation of the application.
    
    This includes:
    - Active states with confidence scores
    - Screenshot of the current screen
    - Screen dimensions
    - Timing metadata
    """
    settings = get_settings()
    
    # Use CLI if configured, otherwise fall back to mock data
    if settings.is_cli_configured:
        try:
            bridge = get_bridge()
            cli_response = bridge.get_observation()
            
            # Convert CLI response to our Pydantic model
            return Observation(
                timestamp=datetime.fromisoformat(cli_response["timestamp"]),
                active_states=[
                    ActiveState(
                        name=s["name"],
                        confidence=s["confidence"],
                        matched_patterns=s.get("matchedPatterns", [])
                    )
                    for s in cli_response.get("activeStates", [])
                ],
                screenshot=cli_response.get("screenshot"),
                screen_width=cli_response["screenWidth"],
                screen_height=cli_response["screenHeight"],
                metadata=cli_response.get("metadata", {})
            )
        except BrobotCLIError as e:
            logger.error(f"CLI error getting observation: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error getting observation: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    # Fall back to mock data
    logger.info("Using mock observation data")
    return get_mock_observation()


@router.post("/execute", response_model=ActionResult, summary="Execute an action")
async def execute_action(request: ActionRequest) -> ActionResult:
    """
    Execute an automation action.
    
    Supported action types:
    - click: Click on an image pattern or location
    - type: Type text at current location
    - drag: Drag from one location to another
    - wait: Wait for a state or condition
    
    The action will be executed by the Brobot automation engine.
    """
    settings = get_settings()
    
    # Use CLI if configured, otherwise fall back to mock data
    if settings.is_cli_configured:
        try:
            bridge = get_bridge()
            
            # Convert request to dict for CLI
            cli_request = {
                "actionType": request.action_type,
                "parameters": request.parameters,
                "targetState": request.target_state,
                "timeout": request.timeout
            }
            
            cli_response = bridge.execute_action(cli_request)
            
            # Convert CLI response to our Pydantic model
            return ActionResult(
                success=cli_response["success"],
                action_type=cli_response["actionType"],
                duration=cli_response["duration"],
                result_state=cli_response.get("resultState"),
                error=cli_response.get("error"),
                metadata=cli_response.get("metadata", {})
            )
        except BrobotCLIError as e:
            logger.error(f"CLI error executing action: {e}")
            # Return error result instead of raising exception
            return ActionResult(
                success=False,
                action_type=request.action_type,
                duration=0.0,
                result_state=None,
                error=str(e),
                metadata={}
            )
        except Exception as e:
            logger.error(f"Unexpected error executing action: {e}")
            return ActionResult(
                success=False,
                action_type=request.action_type,
                duration=0.0,
                result_state=None,
                error="Internal server error",
                metadata={}
            )
    
    # Fall back to mock data
    logger.info("Using mock action execution")
    return get_mock_action_result(request)


@router.get("/health", response_model=HealthStatus, summary="Extended health check")
async def health_check() -> HealthStatus:
    """Get detailed health status including Brobot connection status."""
    settings = get_settings()
    brobot_connected = False
    
    # Check if CLI is available
    if settings.brobot_cli_jar and not settings.use_mock_data:
        try:
            bridge = get_bridge()
            brobot_connected = bridge.is_available()
        except:
            brobot_connected = False
    
    return HealthStatus(
        status="ok",
        version="0.1.0",
        brobot_connected=brobot_connected,
        timestamp=datetime.now()
    )