"""Main FastAPI application for Brobot MCP Server."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

from .api import router as api_router

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
    uvicorn.run(
        "mcp_server.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()