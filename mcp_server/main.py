"""Main FastAPI application for Brobot MCP Server."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

# Create FastAPI instance
app = FastAPI(
    title="Brobot MCP Server",
    description="Model Context Protocol server that allows AI agents to control Brobot automation applications",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


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