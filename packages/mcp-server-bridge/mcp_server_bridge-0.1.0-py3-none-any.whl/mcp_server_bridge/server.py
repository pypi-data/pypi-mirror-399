import json
import platform
import shutil
import os
import argparse
from pathlib import Path
from platformdirs import user_config_dir
from mcp import ServerSession
from mcp.server.fastmcp import Context, FastMCP
import requests
import subprocess
import yaml


def get_safe_path(user_input: str, base_dir: str = ".") -> str:
    """
    处理用户提供的路径参数。

    Args:
        user_input: 用户输入的路径字符串 (例如 "data.txt" 或 "../../etc/passwd")
        base_dir: 允许访问的基础目录，默认为当前目录

    Returns:
        str: 如果安全，返回原始的 user_input

    Raises:
        ValueError: 如果检测到路径穿越企图
    """
    # 1. 初始化基础目录的绝对路径
    base = Path(base_dir).resolve()
    # 2. 将用户输入拼接到基础路径上
    # 注意：如果 user_input 是绝对路径（如 /etc/passwd），joinpath 会忽略 base_dir
    # 因此我们需要先将其处理为相对路径
    normalized_input = user_input.lstrip(os.sep).lstrip('/')
    target = (base / normalized_input).resolve()
    # 3. 检查解析后的路径是否以 base 为前缀
    # is_relative_to 是 Python 3.9+ 的方法
    try:
        target.relative_to(base)
    except ValueError:
        # 如果 target 不在 base 路径下，会抛出 ValueError
        raise ValueError(f"检测到潜在的路径穿越攻击: {user_input}")

    # 4. 验证通过，返回参数本身
    return user_input


def get_shell_executable() -> str:
    """Return a shell/command executable appropriate for the current OS.

    On Windows this prefers `cmd.exe`. On POSIX systems it prefers the user's
    `$SHELL` if available, otherwise checks common shells and falls back to
    `/bin/sh`.
    """
    system = platform.system()
    if system == "Windows":
        return shutil.which("cmd.exe") or shutil.which("cmd") or "cmd.exe"

    # POSIX-like systems
    shell_env = os.environ.get("SHELL")
    candidates = []
    if shell_env:
        candidates.append(shell_env)
    candidates.extend(["/bin/zsh", "/bin/bash", "/bin/sh",
                      "/usr/bin/zsh", "/usr/bin/bash"])
    for c in candidates:
        if shutil.which(c) or os.path.exists(c):
            return c
    return "/bin/sh"


def get_subprocess_prefix() -> list:
    """Return a prefix list suitable for `subprocess` invocations.

    Examples:
    - POSIX: ['/bin/zsh', '-c']
    - Windows: ['cmd.exe', '/c']
    """
    exe = get_shell_executable()
    if platform.system() == "Windows":
        return [exe, "/c"]
    return [exe, "-i", "-c"]


def get_config_dir() -> Path:
    """Get the user configuration directory."""
    config_dir = Path(user_config_dir("mcp-server-bridge"))
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


class McpBridge(FastMCP):
    """Custom MCP Bridge server class.
    To be further expanded
    """

    def list_tools(self):
        return super().list_tools()


def create_app(name: str = "McpBridge"):

    subprocess_prefix = get_subprocess_prefix()

    mcp = McpBridge(name)

    @mcp.tool()
    def get_cli_tool_help(command: str, help_flag: str = "--help"):
        """Get help information for a CLI tool.
        Args:
            command (str): The command name to get help for.
            help_flag (str): The flag to use for help (default: --help).
        Returns:
            str: The help text of the command.
        """
        try:
            cmd = subprocess_prefix + [" ".join([command, help_flag])]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            return e.stderr
        except FileNotFoundError:
            return "Command not found, please check if the command name is correct."
        except Exception as e:
            return f"Error occurred while getting help: {e}"

    @mcp.prompt()
    def register_prompt():
        return (
            "You are connected to the MCP Bridge. You can use various tools available here.\n"
            "Before registering a new tool, the help information for the command (usage and args) must be obtained using the get_cli_tool_help tool provided by mcp and filled in in the register_tool argument.\n"
            "Steps: Call get_cli_tool_help(command=\"< command >\", help_flag=\"--help\") to get the help text. Extract tool_usage and tool_args from the returned help text. Call register_tool(...) to register the tool."
        )

    @mcp.tool()
    async def register_cli_tool(command: str, tool_description: str, tool_usage: str, tool_args: str, ctx: Context[ServerSession, None]):
        """Register a new command line tool with the MCP Bridge.
        Args:
            command (str): The command name to register.
            tool_description (str): A brief description of the tool.
            tool_usage (str): The usage information for the tool.
            tool_args (str): The arguments and options for the tool.
        Returns:
            str: Confirmation message upon successful registration.

        """
        tool = {
            "command": command,
            "description": tool_description,
            "usage": tool_usage,
            "args": tool_args,
        }
        command = get_safe_path(tool['command'])
        out_mcp_yml_file(tool, f"cli_{command}_mcp_tool.yml")
        register_bridge_cli_tool(tool)
        await ctx.session.send_tool_list_changed()
        return f"Tool '{command}' registered successfully."

    @mcp.tool()
    async def register_http_tool(ctx: Context[ServerSession, None], name: str, description: str,  method: str, url: str,  params: str = "{}",  data: str = "{}", headers: str = "{}"):
        """Register a new HTTP tool with the MCP Bridge.
        Args:
            name (str): The name of the HTTP tool.
            description (str): A brief description of the HTTP tool.
            method: type: str , description: HTTP method (GET, POST) , need to be uppercase.
            url: type: str , description: The URL to send the request to.
            params: (optional), type: str , description: Json serialized string Dictionary of URL parameters to append to the URL.
            data: (optional), type: str , description: Json serialized string Dictionary, list of tuples, bytes, or file-like object to send in the body of the request.
            headers: (optional), type: str , description: Json serialized string Dictionary of HTTP Headers to send.

        Returns:
            str: Confirmation message upon successful registration.
        """
        params = json.loads(params) if params else {}
        data = json.loads(data) if data else {}
        headers = json.loads(headers) if headers else {}
        tool = {
            "name": name,
            "description": description,
            "request": {
                "method": method,
                "url": url,
                "params": params,
                "data": data,
                "headers": headers,
            },
        }
        safe_name = get_safe_path(name)
        out_mcp_json_file(tool, f"http_{safe_name}_mcp_tool.json")
        register_bridge_http_tool(tool)
        await ctx.session.send_tool_list_changed()
        return f"HTTP Tool '{safe_name}' registered successfully."

    @mcp.tool()
    async def remove_tool(name: str, ctx: Context[ServerSession, None]):
        """Remove a registered tool from the MCP Bridge.
        Args:
            name (str): The name of the tool to remove.
        Returns:
            str: Confirmation message.
        """
        builtin_tools = ["get_cli_tool_help", "register_cli_tool",
                         "register_http_tool", "remove_tool"]
        if name in builtin_tools:
            return f"Error: Cannot remove builtin tool '{name}'."

        name = get_safe_path(name)
        tools_dir = get_config_dir()

        # Try to find CLI tool config
        cli_config = tools_dir.joinpath(f"cli_{name}_mcp_tool.yml")
        if cli_config.exists():
            cli_config.unlink()
            # Attempt to remove from mcp instance if _tools exists
            if hasattr(mcp, "_tools") and name in mcp._tools:
                del mcp._tools[name]

            await ctx.session.send_tool_list_changed()
            return f"CLI Tool '{name}' removed successfully."

        # Try to find HTTP tool config
        http_config = tools_dir.joinpath(f"http_{name}_mcp_tool.json")
        if http_config.exists():
            http_config.unlink()

            if hasattr(mcp, "_tools") and name in mcp._tools:
                del mcp._tools[name]

            await ctx.session.send_tool_list_changed()
            return f"HTTP Tool '{name}' removed successfully."

        return f"Error: Tool '{name}' not found."

    def out_mcp_yml_file(data, file_name):
        tools_dir = get_config_dir()
        target = tools_dir.joinpath(file_name)
        with target.open("w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True,
                      default_flow_style=False)

    def out_mcp_json_file(data, file_name):
        tools_dir = get_config_dir()
        target = tools_dir.joinpath(file_name)
        with target.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def general_invoke(tool_path: str, args: str):
        try:
            cmd = subprocess_prefix + [tool_path + " " + args]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            return e.stderr
        except FileNotFoundError:
            return "Command not found, please check if the command name is correct."

    def execute_request(method: str, url: str, params="{}", data="{}", headers="{}"):
        data = json.loads(data) if data else None
        params = json.loads(params) if params else None
        headers = json.loads(headers) if headers else None
        try:
            response = requests.request(
                method=method.upper(), url=url, params=params, data=data, headers=headers, timeout=15, verify=False, allow_redirects=False)
            response.raise_for_status()
            return response.text
        except Exception as e:
            return {"error": str(e)}

    cli_tools_description = """Invoke a command line tool with given arguments.
    Example args: (tool_path="whoami", args="-a -b")

    All command line tools description :
    ---------------
    {tool_description}
    ---------------

    returns:
    The standard output of the command if successful,
    otherwise returns the standard error output.
    """

    http_tools_description = """If there is a placeholder {{}} in the argument, it needs to be replaced with the actual argument or removed. 
    
    HTTP tools description :
    ---------------
    {tool_description}
    ---------------

    Params description : 
    ---------------
    method: type: str , description: HTTP method (GET, POST) , need to be uppercase.
    url: type: str , description: The URL to send the request to.
    params: (optional), type: str , description: Json serialized string Dictionary of URL parameters to append to the URL.
    data: (optional), type: str , description: Json serialized string Dictionary, list of tuples, bytes, or file-like object to send in the body of the request.
    headers: (optional), type: str , description: Json serialized string Dictionary of HTTP Headers to send.
    ---------------

    Target API  information :
    ---------------
    {request_description}
    ---------------

    returns:
    The txt response from the HTTP request if successful,
    otherwise returns an error message.
    """

    def register_bridge_cli_tool(tool):
        mcp.add_tool(
            general_invoke,
            name=tool["command"],
            title=tool["description"],
            description=cli_tools_description.format(
                tool_description=tool["args"])
        )

    def register_bridge_http_tool(tool):
        mcp.add_tool(
            execute_request,
            name=tool["name"],
            title=tool["description"],
            description=http_tools_description.format(
                tool_description=str(tool['description']),
                request_description=yaml.dump(
                    tool['request'], default_flow_style=False, allow_unicode=True)
            )
        )

    def load_yml_file_tools():
        try:
            tools_dir = get_config_dir()
            if tools_dir.is_dir():
                for entry in tools_dir.iterdir():
                    if entry.name.endswith("mcp_tool.yml"):
                        content = entry.read_text(encoding="utf-8")
                        tool = yaml.load(content, Loader=yaml.FullLoader)
                        register_bridge_cli_tool(tool)
        except Exception as e:
            print(f"Failed to load tools from config dir: {e}")

    def load_json_file_tools():
        try:
            tools_dir = get_config_dir()
            if tools_dir.is_dir():
                for entry in tools_dir.iterdir():
                    if entry.name.endswith("mcp_tool.json"):
                        with entry.open("r", encoding="utf-8") as f:
                            tools = json.load(f)
                            for tool in tools if isinstance(tools, list) else [tools]:
                                register_bridge_http_tool(tool)
        except Exception as e:
            print(f"Failed to load tools from config dir: {e}")

    load_yml_file_tools()
    load_json_file_tools()
    return mcp


def main():
    parser = argparse.ArgumentParser(description="MCP Bridge Server")
    parser.add_argument(
        "-t", "--transport",
        default="stdio",
        choices=["stdio", "sse"],
        help="Transport mode: stdio or sse"
    )
    args = parser.parse_args()

    mcp = create_app()
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
