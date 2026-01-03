"""MCP server discovery and schema retrieval utility."""

import time
from typing import Any

import httpx

# Timeout constants
REMOTE_MCP_TIMEOUT = 30
LOCAL_MCP_TIMEOUT = 30  # Increased for stdio transport spawning

# Cache constants
CACHE_TTL = 300  # 5 minutes TTL for tool schemas


class RemoteMCPClient:
    """Client for remote MCP servers via MCP ACI service."""

    def __init__(
        self,
        api_key: str,
        linked_account_owner_id: str,
        base_url: str = "https://mcp.realtimex.ai",
    ):
        self.api_key = api_key
        self.linked_account_owner_id = linked_account_owner_id
        self.base_url = base_url

    def list_servers(self) -> list[dict[str, Any]]:
        """List active remote MCP servers with their actions."""
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }
        params = {"linked_account_owner_id": self.linked_account_owner_id}

        with httpx.Client() as client:
            # Get linked accounts
            response = client.get(
                f"{self.base_url}/v1/linked-accounts",
                headers=headers,
                params=params,
                timeout=REMOTE_MCP_TIMEOUT,
            )
            response.raise_for_status()
            linked_accounts = response.json()

            servers = []
            for account in linked_accounts:
                if account.get("enabled", False):
                    server_id = account["app_name"]

                    # Get actions for this server
                    try:
                        app_response = client.get(
                            f"{self.base_url}/v1/apps/{server_id}",
                            headers=headers,
                            timeout=REMOTE_MCP_TIMEOUT,
                        )
                        app_response.raise_for_status()
                        app_data = app_response.json()

                        # Filter only active functions
                        actions = [
                            {
                                "name": func["name"],
                                "description": func.get("description", ""),
                            }
                            for func in app_data.get("functions", [])
                            if func.get("active", False)
                        ]
                    except Exception:
                        actions = []

                    servers.append(
                        {
                            "server_id": server_id,
                            "provider": "remote",
                            "description": app_data.get("description", ""),
                            "actions": actions,
                        }
                    )

            return servers

    def get_action_schema(self, server_id: str, action_id: str) -> dict[str, Any]:
        """Get schema for a specific remote MCP action."""
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }

        with httpx.Client() as client:
            response = client.get(
                f"{self.base_url}/v1/functions/{action_id}/definition",
                headers=headers,
                params={"format": "openai"},
                timeout=REMOTE_MCP_TIMEOUT,
            )
            response.raise_for_status()

        action_data = response.json()

        if action_data.get("type") != "function":
            raise ValueError(f"Invalid action definition for action '{action_id}'")

        action_def = action_data["function"]
        return {
            "server_id": server_id,
            "action_id": action_id,
            "provider": "remote",
            "description": action_def.get("description", ""),
            "parameters": action_def.get("parameters", {}),
        }


class LocalMCPClient:
    """Client for local MCP servers."""

    def __init__(self, base_url: str = "http://localhost:3001"):
        self.base_url = base_url
        self._server_tools_cache: dict[str, tuple[list[dict[str, Any]], float]] = {}

    def _filter_enabled_tools(
        self, tools: list[dict[str, Any]], enabled_tools: list[str]
    ) -> list[dict[str, Any]]:
        """Filter tools based on enabled_tools configuration."""
        if enabled_tools == ["*"]:
            return tools  # All tools enabled

        # Filter to only enabled tools
        return [tool for tool in tools if tool.get("name") in enabled_tools]

    def list_servers(self) -> list[dict[str, Any]]:
        """List active local MCP servers with their actions."""
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.base_url}/api/mcp-servers/local?configured=true",
                    timeout=LOCAL_MCP_TIMEOUT,
                )
                response.raise_for_status()
                data = response.json()

                if not data.get("success"):
                    return []

                servers = []
                for server in data.get("servers", []):
                    server_id = server.get("name") or server.get("id")
                    enabled = server.get("enabled", False)
                    tools = server.get("tools", [])
                    enabled_tools = server.get("enabled_tools", ["*"])

                    # Skip disabled servers
                    if not enabled:
                        continue

                    # If tools exist, use them directly
                    if tools:
                        # Filter tools based on enabled_tools configuration
                        filtered_tools = self._filter_enabled_tools(
                            tools, enabled_tools
                        )
                        actions = [
                            {
                                "name": tool["name"],
                                "description": tool.get("description", ""),
                            }
                            for tool in filtered_tools
                        ]
                        # Cache the original tools for later schema requests
                        self._server_tools_cache[server_id] = (tools, time.time())
                    else:
                        # Make follow-up request for tools
                        try:
                            tools_response = client.get(
                                f"{self.base_url}/api/mcp-servers/local/{server_id}/tools",
                                timeout=LOCAL_MCP_TIMEOUT,
                            )
                            tools_response.raise_for_status()
                            tools_data = tools_response.json()

                            if tools_data.get("success"):
                                fetched_tools = tools_data.get("tools", [])
                                # Filter tools based on enabled_tools configuration
                                filtered_tools = self._filter_enabled_tools(
                                    fetched_tools, enabled_tools
                                )
                                actions = [
                                    {
                                        "name": tool["name"],
                                        "description": tool.get("description", ""),
                                    }
                                    for tool in filtered_tools
                                ]
                                # Cache the original tools for later schema requests
                                self._server_tools_cache[server_id] = (
                                    fetched_tools,
                                    time.time(),
                                )
                            else:
                                actions = []
                        except Exception:
                            actions = []

                    servers.append(
                        {
                            "server_id": server_id,
                            "provider": "local",
                            "description": server.get("description", ""),
                            "actions": actions,
                        }
                    )

                return servers
        except Exception:
            return []

    def get_action_schema(self, server_id: str, action_id: str) -> dict[str, Any]:
        """Get schema for a specific local MCP action, using cached data when available."""
        current_time = time.time()

        # Check if we have cached tools for this server
        if server_id in self._server_tools_cache:
            tools, timestamp = self._server_tools_cache[server_id]
            if current_time - timestamp < CACHE_TTL:
                # Look for the tool in cached data
                for tool in tools:
                    if tool.get("name") == action_id:
                        # Handle both inputSchema (listing) and input_schema (specific) field names
                        input_schema = tool.get("input_schema") or tool.get(
                            "inputSchema"
                        )
                        if input_schema:
                            return {
                                "server_id": server_id,
                                "action_id": action_id,
                                "provider": "local",
                                "description": tool.get("description", ""),
                                "parameters": input_schema,
                            }

        # Cache miss or incomplete data, fetch from API
        with httpx.Client() as client:
            response = client.get(
                f"{self.base_url}/api/mcp-servers/local/{server_id}/tools/{action_id}",
                timeout=LOCAL_MCP_TIMEOUT,
            )
            response.raise_for_status()

        data = response.json()

        if not data.get("success"):
            raise ValueError(f"Failed to get schema for tool '{action_id}'")

        tool = data.get("tool", {})
        return {
            "server_id": server_id,
            "action_id": action_id,
            "provider": "local",
            "description": tool.get("description", ""),
            "parameters": tool.get("input_schema", {}),
        }


class MCPHelper:
    """Unified interface for remote and local MCP server discovery."""

    def __init__(
        self, remote_config: dict | None = None, local_config: dict | None = None
    ):
        self.remote_client = RemoteMCPClient(**remote_config) if remote_config else None
        self.local_client = LocalMCPClient(**local_config) if local_config else None

    def list_all_servers(self) -> list[dict[str, Any]]:
        """Get servers from all available providers."""
        servers = []

        if self.remote_client:
            try:
                servers.extend(self.remote_client.list_servers())
            except Exception:
                pass  # Graceful degradation

        if self.local_client:
            try:
                servers.extend(self.local_client.list_servers())
            except Exception:
                pass  # Graceful degradation

        return servers

    def get_action_schema(self, server_id: str, action_id: str) -> dict[str, Any]:
        """Get action schema with auto-detection of provider."""
        # Try remote first, then local
        if self.remote_client:
            try:
                return self.remote_client.get_action_schema(server_id, action_id)
            except Exception:
                pass

        if self.local_client:
            try:
                return self.local_client.get_action_schema(server_id, action_id)
            except Exception:
                pass

        raise ValueError(f"Action '{action_id}' not found on server '{server_id}'")
