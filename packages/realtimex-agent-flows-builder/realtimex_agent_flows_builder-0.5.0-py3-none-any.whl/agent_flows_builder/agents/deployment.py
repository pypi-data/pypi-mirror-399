"""LangGraph deployment module - creates agent for langgraph.json."""

from __future__ import annotations

import os

from agent_flows_builder.agents.flow_builder_master import create_flow_builder_agent


def _require_env(key: str) -> str:
    value = os.getenv(key, "").strip()
    if not value:
        raise RuntimeError(
            f"Missing required environment variable '{key}' for LangGraph deployment."
        )
    return value


# This is only for LangGraph deployment - creates agent at import time
agent = create_flow_builder_agent(
    realtimex_ai_api_key=_require_env("REALTIMEX_AI_API_KEY"),
    realtimex_ai_base_path=_require_env("REALTIMEX_AI_BASE_PATH"),
    mcp_aci_api_key=_require_env("MCP_ACI_API_KEY"),
    mcp_aci_linked_account_owner_id=_require_env("MCP_ACI_LINKED_ACCOUNT_OWNER_ID"),
)
