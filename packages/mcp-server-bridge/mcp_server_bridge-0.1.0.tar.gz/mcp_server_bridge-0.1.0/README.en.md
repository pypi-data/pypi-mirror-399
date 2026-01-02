# MCP Server Bridge
[中文](./README.md) | [English](./README.en.md)

A Model Context Protocol (MCP) server bridge that allows dynamic registration of CLI tools and HTTP requests as MCP tools.

## Features

- **Dynamic Tool Registration**:
  - **CLI Tools**: Register any CLI tool available in the environment.
  - **HTTP Tools**: Register simple HTTP endpoints as tools.
- **Configuration Persistence**:
  - CLI tools are persisted as YAML configurations.
  - HTTP tools are persisted as JSON configurations.
- **Examples**: The following APIs and CLI tools can be registered via LLM conversations:
  - **CLI**: `fscan`, `httpx`, `naabu`, `nmap`, `nuclei`, `subfinder`
  - **HTTP**: `http://cip.cc`

## Installation

1. Install `uv` (if not installed):
```bash
pip install uv
```

2. Install dependencies and packages:
```bash
uv sync
```

3. Run the server:
```bash
uv run mcp-server-bridge
```

## Usage

### Connecting to the Server

The server runs in stdio or SSE mode.

### Built-in Management Tools

1. `get_cli_tool_help(command, help_flag)`:
   - Get help text for a CLI command.
   - Used to determine arguments during registration.
2. `register_cli_tool(command, tool_description, tool_usage, tool_args)`:
   - Register a new CLI tool to expose via MCP.
   - Generates YAML configuration in `src/mcp_server_bridge/config/`.
3. `register_http_tool(name, description, method, url, params, data, headers)`:
   - Register a new HTTP tool.
   - Generates JSON configuration in `src/mcp_server_bridge/config/`.

### Usage Examples

#### Register CLI Tool

Register a CLI tool `fscan` as an `MCP` tool:

![alt text](docs/cli_tool_register.png)

CLI tool usage:
![alt text](docs/cli_tool_call.png)

#### Register HTTP Tool

Register an HTTP interface as an `MCP` tool:
![alt text](docs/http_tool_register.png)

HTTP tool usage:
![alt text](docs/http_tool_call.png)

## Project Structure

- `src/mcp_server_bridge/`: Main package source.
  - `server.py`: Core server logic and tool definitions.
  - `config/`: Directory for storing registered tool configurations (YAML/JSON).
  - `__init__.py`: Package exports.
  - `__main__.py`: Entry point.
- `tests/`: Test suite.

## Development

Run tests:
```bash
uv run pytest
```
