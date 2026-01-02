import pytest
import asyncio
from mcp_server_bridge.server import create_app


def test_create_app():
    mcp = create_app()
    assert mcp is not None
    assert mcp.name == "McpBridge"


def test_list_tools():
    mcp = create_app()
    # FastMCP.list_tools is async
    tools = asyncio.run(mcp.list_tools())
    # We expect at least get_cli_tool_help and register_tool
    tool_names = [t.name for t in tools]
    assert "get_cli_tool_help" in tool_names
    assert "register_cli_tool" in tool_names


def test_remove_tool_registered():
    mcp = create_app()
    tools = asyncio.run(mcp.list_tools())
    tool_names = [t.name for t in tools]
    assert "remove_tool" in tool_names
