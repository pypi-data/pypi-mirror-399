"""MCP server discovery tools for Agent Flows Builder."""

import json

from langchain.tools import ToolRuntime, tool
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from agent_flows_builder.utils.mcp_helper import MCPHelper

# Global MCP helper instance - set by create_flow_builder_agent
_mcp_helper: MCPHelper | None = None


def configure_mcp_tools(
    api_key: str,
    linked_account_owner_id: str,
    local_mcp_base_url: str = "http://localhost:3001",
) -> None:
    """Configure MCP tools with required credentials."""
    global _mcp_helper  # noqa: PLW0602, PLW0603

    remote_config = {
        "api_key": api_key,
        "linked_account_owner_id": linked_account_owner_id,
    }

    local_config = {"base_url": local_mcp_base_url}

    _mcp_helper = MCPHelper(remote_config=remote_config, local_config=local_config)


@tool
def list_mcp_servers(
    runtime: ToolRuntime,
) -> Command:
    """List user's configured MCP servers with their available actions."""
    try:
        if not _mcp_helper:
            raise ValueError("MCP helper not configured")

        servers = _mcp_helper.list_all_servers()
        result = {"servers": servers}

        # Create descriptive message
        remote_count = sum(1 for s in servers if s["provider"] == "remote")
        local_count = sum(1 for s in servers if s["provider"] == "local")

        if servers:
            parts = []
            if remote_count:
                parts.append(f"{remote_count} remote")
            if local_count:
                parts.append(f"{local_count} local")
            message = f"Found {len(servers)} MCP servers ({', '.join(parts)})"
        else:
            message = "No MCP servers configured"

        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"{message}\n{json.dumps(result)}",
                        tool_call_id=runtime.tool_call_id,
                    )
                ],
            }
        )

    except Exception as e:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Error: Failed to list MCP servers - {str(e)}",
                        tool_call_id=runtime.tool_call_id,
                    )
                ],
            }
        )


@tool
def get_mcp_action_schema(
    server_id: str,
    action_id: str,
    runtime: ToolRuntime,
) -> Command:
    """Get detailed schema for a specific MCP action."""
    try:
        if not _mcp_helper:
            raise ValueError("MCP helper not configured")

        schema = _mcp_helper.get_action_schema(server_id, action_id)
        message = f"Schema for action '{action_id}' on {schema['provider']} server '{server_id}'"

        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"{message}\n{json.dumps(schema)}",
                        tool_call_id=runtime.tool_call_id,
                    )
                ],
            }
        )

    except Exception as e:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Error: Failed to get MCP action schema - {str(e)}",
                        tool_call_id=runtime.tool_call_id,
                    )
                ],
            }
        )
