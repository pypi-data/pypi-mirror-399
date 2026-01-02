"""
MCP Client Connector

Connects to MCP servers and retrieves their tool definitions.

This is the "plumbing" that talks to actual MCP servers to get
their tools so we can scan them.
"""

import asyncio
import json
import os
import platform
from pathlib import Path
from typing import Optional

from guardfive.models import MCPServer, Tool


# Common config file locations
import platform

def _get_config_paths() -> list[Path]:
    """Get config paths based on operating system"""
    home = Path.home()
    paths = []
    
    # Cursor (same on all platforms)
    paths.append(home / ".cursor" / "mcp.json")
    
    if platform.system() == "Windows":
        # Windows paths
        appdata = Path(os.environ.get("APPDATA", home / "AppData/Roaming"))
        localappdata = Path(os.environ.get("LOCALAPPDATA", home / "AppData/Local"))
        
        paths.extend([
            appdata / "Claude" / "claude_desktop_config.json",
            appdata / "Windsurf" / "mcp.json",
            appdata / "Code" / "User" / "mcp.json",
            localappdata / "Cursor" / "mcp.json",
        ])
    elif platform.system() == "Darwin":
        # macOS paths
        paths.extend([
            home / "Library/Application Support/Claude/claude_desktop_config.json",
            home / "Library/Application Support/Windsurf/mcp.json",
            home / "Library/Application Support/Code/User/mcp.json",
        ])
    else:
        # Linux paths
        paths.extend([
            home / ".config/claude/claude_desktop_config.json",
            home / ".config/windsurf/mcp.json",
            home / ".config/Code/User/mcp.json",
        ])
    
    return paths

CONFIG_PATHS = _get_config_paths()


def find_config_files() -> list[Path]:
    """Find all MCP config files on this system"""
    found = []
    for path in CONFIG_PATHS:
        if path.exists():
            found.append(path)
    return found


def get_checked_paths() -> list[Path]:
    """Return list of paths we check (for display purposes)"""
    return CONFIG_PATHS


def parse_config_file(config_path: Path) -> list[MCPServer]:
    """
    Parse an MCP config file and return list of servers.
    
    Config files look like:
    {
        "mcpServers": {
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
            }
        }
    }
    """
    with open(config_path) as f:
        config = json.load(f)
    
    servers = []
    mcp_servers = config.get("mcpServers", {})
    
    for name, server_config in mcp_servers.items():
        server = MCPServer(
            name=name,
            command=server_config.get("command", ""),
            args=server_config.get("args", []),
            env=server_config.get("env", {}),
        )
        servers.append(server)
    
    return servers


async def fetch_tools_from_server(server: MCPServer) -> list[Tool]:
    """
    Connect to an MCP server and fetch its tool definitions.
    
    This starts the server process, asks for its tools, then shuts it down.
    """
    # For now, return mock data - we'll implement real MCP connection next
    # This requires the MCP SDK which we'll add in the next iteration
    
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        
        # Create server parameters
        server_params = StdioServerParameters(
            command=server.command,
            args=server.args,
            env=server.env if server.env else None,
        )
        
        tools = []
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                
                # Get list of tools
                tools_response = await session.list_tools()
                
                for tool_def in tools_response.tools:
                    tool = Tool(
                        name=tool_def.name,
                        description=tool_def.description or "",
                        parameters=tool_def.inputSchema if hasattr(tool_def, 'inputSchema') else {},
                        server_name=server.name,
                    )
                    tools.append(tool)
        
        return tools
        
    except ImportError:
        # MCP SDK not installed, return mock data for testing
        return _get_mock_tools(server)
    except Exception as e:
        # Connection failed, return empty with error note
        print(f"Warning: Could not connect to server '{server.name}': {e}")
        return []


def _get_mock_tools(server: MCPServer) -> list[Tool]:
    """Return mock tools for testing when MCP SDK is not available"""
    return [
        Tool(
            name="example_tool",
            description=f"Example tool from {server.name}",
            parameters={"type": "object", "properties": {}},
            server_name=server.name,
        )
    ]


async def fetch_all_tools(servers: list[MCPServer]) -> list[Tool]:
    """Fetch tools from all servers"""
    all_tools = []
    
    for server in servers:
        try:
            tools = await fetch_tools_from_server(server)
            all_tools.extend(tools)
        except Exception as e:
            print(f"Error fetching tools from {server.name}: {e}")
    
    return all_tools


# Sync wrapper for easier use
def fetch_tools_sync(servers: list[MCPServer]) -> list[Tool]:
    """Synchronous wrapper for fetch_all_tools"""
    return asyncio.run(fetch_all_tools(servers))
