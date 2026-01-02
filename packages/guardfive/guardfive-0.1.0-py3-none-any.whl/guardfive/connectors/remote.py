"""
Remote MCP Server Connector

Connects to remote MCP servers over HTTP/HTTPS to fetch their tools.

MCP servers can expose HTTP endpoints that accept JSON-RPC style messages.
This connector sends a tools/list request and parses the response.
"""

import httpx
from typing import Optional
from guardfive.models import Tool


def fetch_remote_tools(
    url: str, 
    timeout: float = 30.0,
    headers: Optional[dict] = None
) -> list[Tool]:
    """
    Connect to a remote MCP server and fetch its tools.
    
    Args:
        url: Base URL of the MCP server (e.g., https://mcp.company.com)
        timeout: Request timeout in seconds
        headers: Optional headers (e.g., for authentication)
    
    Returns:
        List of Tool objects from the server
    
    Raises:
        ConnectionError: If unable to connect to server
        ValueError: If response is invalid
    """
    tools = []
    
    # Prepare headers
    request_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if headers:
        request_headers.update(headers)
    
    # MCP uses JSON-RPC style messages
    # The tools/list method returns available tools
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    
    # Try different endpoint patterns
    endpoints_to_try = [
        url,  # Direct URL
        f"{url.rstrip('/')}/mcp",  # /mcp endpoint
        f"{url.rstrip('/')}/api/mcp",  # /api/mcp endpoint
        f"{url.rstrip('/')}/v1/mcp",  # /v1/mcp endpoint
    ]
    
    last_error = None
    
    for endpoint in endpoints_to_try:
        try:
            tools = _try_fetch_tools(endpoint, payload, request_headers, timeout)
            if tools:
                return tools
        except Exception as e:
            last_error = e
            continue
    
    # If all endpoints failed, try to get tools from OpenAPI/schema
    try:
        tools = _try_fetch_from_openapi(url, request_headers, timeout)
        if tools:
            return tools
    except Exception:
        pass
    
    if last_error:
        raise ConnectionError(f"Failed to fetch tools from {url}: {last_error}")
    
    return tools


def _try_fetch_tools(
    endpoint: str, 
    payload: dict, 
    headers: dict, 
    timeout: float
) -> list[Tool]:
    """Try to fetch tools from a specific endpoint"""
    tools = []
    
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        response = client.post(endpoint, json=payload, headers=headers)
        
        # These status codes mean "try next endpoint" not "fail completely"
        if response.status_code in [404, 405, 415, 501]:
            return []  # Try next endpoint
        
        response.raise_for_status()
        data = response.json()
        
        # Parse JSON-RPC response
        if "result" in data:
            result = data["result"]
            tool_list = result.get("tools", [])
            
            for tool_data in tool_list:
                tool = Tool(
                    name=tool_data.get("name", "unknown"),
                    description=tool_data.get("description", ""),
                    parameters=tool_data.get("inputSchema", {}).get("properties", {}),
                    server_name=_extract_server_name(endpoint),
                )
                tools.append(tool)
        
        # Some servers return tools directly
        elif "tools" in data:
            for tool_data in data["tools"]:
                tool = Tool(
                    name=tool_data.get("name", "unknown"),
                    description=tool_data.get("description", ""),
                    parameters=tool_data.get("inputSchema", {}).get("properties", {}),
                    server_name=_extract_server_name(endpoint),
                )
                tools.append(tool)
    
    return tools


def _try_fetch_from_openapi(url: str, headers: dict, timeout: float) -> list[Tool]:
    """Try to fetch tools from OpenAPI/Swagger schema"""
    tools = []
    
    openapi_endpoints = [
        f"{url.rstrip('/')}/openapi.json",
        f"{url.rstrip('/')}/swagger.json",
        f"{url.rstrip('/')}/api/openapi.json",
        f"{url.rstrip('/')}/.well-known/openapi.json",
    ]
    
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        for endpoint in openapi_endpoints:
            try:
                response = client.get(endpoint, headers=headers)
                if response.status_code != 200:
                    continue
                
                data = response.json()
                
                # Parse OpenAPI paths as tools
                paths = data.get("paths", {})
                for path, methods in paths.items():
                    for method, details in methods.items():
                        if method.lower() in ["get", "post", "put", "delete"]:
                            tool = Tool(
                                name=details.get("operationId", path.replace("/", "_")),
                                description=details.get("summary", "") or details.get("description", ""),
                                parameters=_extract_openapi_params(details),
                                server_name=_extract_server_name(url),
                            )
                            tools.append(tool)
                
                if tools:
                    return tools
                    
            except Exception:
                continue
    
    return tools


def _extract_openapi_params(operation: dict) -> dict:
    """Extract parameters from OpenAPI operation"""
    params = {}
    
    # Query/path parameters
    for param in operation.get("parameters", []):
        params[param.get("name", "unknown")] = param.get("schema", {}).get("type", "string")
    
    # Request body
    request_body = operation.get("requestBody", {})
    content = request_body.get("content", {})
    json_content = content.get("application/json", {})
    schema = json_content.get("schema", {})
    properties = schema.get("properties", {})
    
    for prop_name, prop_details in properties.items():
        params[prop_name] = prop_details.get("type", "string")
    
    return params


def _extract_server_name(url: str) -> str:
    """Extract a readable server name from URL"""
    # Remove protocol
    name = url.replace("https://", "").replace("http://", "")
    # Remove path
    name = name.split("/")[0]
    # Remove port
    name = name.split(":")[0]
    return name


def check_server_reachable(url: str, timeout: float = 10.0) -> tuple[bool, str]:
    """
    Check if a server is reachable.
    
    Returns:
        Tuple of (is_reachable, message)
    """
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(url)
            return True, f"Server responded with status {response.status_code}"
    except httpx.ConnectError:
        return False, "Could not connect to server"
    except httpx.TimeoutException:
        return False, "Connection timed out"
    except Exception as e:
        return False, f"Error: {str(e)}"