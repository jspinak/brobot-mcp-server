"""Main FastAPI application for Brobot MCP Server."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import logging

from .api import router as api_router
from .config import get_settings
from .brobot_bridge import initialize_bridge

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI instance
app = FastAPI(
    title="Brobot MCP Server",
    description="Model Context Protocol server that allows AI agents to control Brobot automation applications",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Include API routes
app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    settings = get_settings()
    
    if settings.brobot_cli_jar and not settings.use_mock_data:
        try:
            initialize_bridge(
                jar_path=settings.brobot_cli_jar,
                java_executable=settings.java_executable
            )
            logger.info("Brobot bridge initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Brobot bridge: {e}")
            logger.info("Server will continue with mock data")
    else:
        logger.info("Running in mock data mode (CLI not configured)")


@app.get("/health", response_model=dict)
async def health_check() -> dict:
    """Health check endpoint to verify server is running."""
    return {"status": "ok"}


@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "name": "Brobot MCP Server",
        "version": "0.1.0",
        "description": "Model Context Protocol server for Brobot automation",
        "docs": "/docs",
        "health": "/health",
        "api": {
            "state_structure": "/api/v1/state_structure",
            "observation": "/api/v1/observation",
            "execute": "/api/v1/execute"
        }
    }


def main():
    """Run the FastAPI server."""
    settings = get_settings()
    
    uvicorn.run(
        "mcp_server.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level,
    )


if __name__ == "__main__":
    main()