#!/usr/bin/env python3
"""Asynchronous usage example of the Brobot client library."""

import asyncio
import logging
from datetime import datetime
from brobot_client import AsyncBrobotClient, Location

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


async def monitor_state_changes(client, duration=10):
    """Monitor state changes for a specified duration."""
    logger.info(f"Monitoring state changes for {duration} seconds...")
    
    start_time = datetime.now()
    previous_states = set()
    
    while (datetime.now() - start_time).total_seconds() < duration:
        observation = await client.get_observation()
        current_states = {s.name for s in observation.active_states}
        
        # Check for state changes
        new_states = current_states - previous_states
        lost_states = previous_states - current_states
        
        if new_states:
            logger.info(f"New states detected: {new_states}")
        if lost_states:
            logger.info(f"States deactivated: {lost_states}")
        
        previous_states = current_states
        await asyncio.sleep(1.0)
    
    logger.info("Monitoring completed")


async def perform_parallel_actions(client):
    """Demonstrate parallel action execution."""
    logger.info("Executing actions in parallel...")
    
    # Define actions to perform
    actions = [
        client.click(location=Location(x=100, y=100)),
        client.click(location=Location(x=200, y=200)),
        client.click(location=Location(x=300, y=300)),
    ]
    
    # Execute all actions concurrently
    results = await asyncio.gather(*actions, return_exceptions=True)
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Action {i+1} failed: {result}")
        else:
            logger.info(f"Action {i+1} completed in {result.duration:.2f}s")


async def automated_workflow(client):
    """Example of an automated workflow."""
    logger.info("Starting automated workflow...")
    
    try:
        # Step 1: Get initial state
        observation = await client.get_observation()
        initial_state = observation.get_most_confident_state()
        logger.info(f"Initial state: {initial_state.name if initial_state else 'Unknown'}")
        
        # Step 2: Navigate to login if needed
        if initial_state and initial_state.name == "main_menu":
            logger.info("Navigating to login screen...")
            await client.click(image_pattern="login_button.png")
            await asyncio.sleep(1.0)  # Wait for transition
        
        # Step 3: Perform login
        logger.info("Performing login...")
        
        # Enter username
        await client.click(image_pattern="username_field.png")
        await client.type_text("demo_user")
        
        # Enter password
        await client.click(image_pattern="password_field.png")
        await client.type_text("demo_password")
        
        # Submit
        await client.click(image_pattern="submit_button.png")
        
        # Step 4: Wait for dashboard
        logger.info("Waiting for dashboard...")
        await client.wait_for_state("dashboard", timeout=30.0)
        
        logger.info("Workflow completed successfully!")
        
    except Exception as e:
        logger.error(f"Workflow failed: {e}")


async def main():
    """Main async function demonstrating various features."""
    
    # Create async client
    async with AsyncBrobotClient() as client:
        
        # Check server health
        health = await client.get_health()
        logger.info(f"Server health: {health}")
        
        # Get state structure
        state_structure = await client.get_state_structure()
        logger.info(f"Application has {len(state_structure.states)} states")
        
        # Run different examples
        tasks = [
            # Monitor states in background
            asyncio.create_task(monitor_state_changes(client, duration=5)),
            
            # Perform some parallel actions
            asyncio.create_task(perform_parallel_actions(client)),
            
            # Run automated workflow
            asyncio.create_task(automated_workflow(client))
        ]
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info("All tasks completed!")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())