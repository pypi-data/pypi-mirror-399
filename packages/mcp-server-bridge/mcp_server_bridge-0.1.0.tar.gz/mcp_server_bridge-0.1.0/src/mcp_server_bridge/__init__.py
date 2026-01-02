"""mcp_bridge package

Provides creation and entrypoint for the MCP Bridge server.
"""
from .server import create_app, main

__all__ = ["create_app", "main"]
