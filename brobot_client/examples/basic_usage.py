#!/usr/bin/env python3
"""Basic usage example of the Brobot client library."""

from brobot_client import BrobotClient, Location
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Demonstrate basic client usage."""
    
    # Create client - will connect to localhost:8000 by default
    with BrobotClient() as client:
        
        # 1. Check server health
        logger.info("Checking server health...")
        health = client.get_health()
        logger.info(f"Server status: {health['status']}")
        logger.info(f"Brobot connected: {health['brobot_connected']}")
        
        # 2. Get state structure
        logger.info("\nGetting application state structure...")
        state_structure = client.get_state_structure()
        logger.info(f"Found {len(state_structure.states)} states:")
        
        for state in state_structure.states:
            logger.info(f"  - {state.name}: {state.description}")
            if state.is_initial:
                logger.info(f"    (Initial state)")
        
        # 3. Get current observation
        logger.info("\nGetting current observation...")
        observation = client.get_observation()
        logger.info(f"Screen size: {observation.screen_width}x{observation.screen_height}")
        logger.info(f"Active states:")
        
        for active_state in observation.active_states:
            logger.info(f"  - {active_state.name}: {active_state.confidence:.2%} confidence")
        
        # Save screenshot if available
        if observation.screenshot:
            if observation.save_screenshot("screenshot.png"):
                logger.info("Screenshot saved to screenshot.png")
        
        # 4. Perform some actions
        logger.info("\nPerforming actions...")
        
        try:
            # Click on a button
            logger.info("Clicking on login button...")
            result = client.click(image_pattern="login_button.png")
            logger.info(f"Click completed in {result.duration:.2f}s")
            
        except Exception as e:
            logger.warning(f"Click failed: {e}")
            
            # Try clicking at a specific location instead
            logger.info("Clicking at specific coordinates...")
            result = client.click(location=Location(x=640, y=480))
            logger.info(f"Click at location completed")
        
        try:
            # Type some text
            logger.info("Typing text...")
            result = client.type_text("Hello from Brobot client!")
            logger.info(f"Typing completed in {result.duration:.2f}s")
            
        except Exception as e:
            logger.warning(f"Typing failed: {e}")
        
        # 5. Wait for a specific state
        try:
            logger.info("Waiting for dashboard state...")
            result = client.wait_for_state("dashboard", timeout=10.0)
            logger.info(f"State reached in {result.duration:.2f}s")
            
        except Exception as e:
            logger.warning(f"Wait failed: {e}")
        
        logger.info("\nDemo completed!")


if __name__ == "__main__":
    main()