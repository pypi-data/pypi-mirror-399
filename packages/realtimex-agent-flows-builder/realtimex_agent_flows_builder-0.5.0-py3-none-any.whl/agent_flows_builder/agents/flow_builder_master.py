"""Flow Builder Master Agent implementation using Deep Agents framework.

This module creates the main AI agent for building workflow automations via natural language.
Uses a master-specialist architecture with configurable models and settings.
"""

from pathlib import Path

from deepagents.realtimex_graph import create_realtimex_deep_agent

from agent_flows_builder.agents.sub_agents import (
    create_configuration_expert,
    create_flow_architect,
    create_flow_validator,
)
from agent_flows_builder.config.settings import ModelProviderConfig
from agent_flows_builder.middleware import (
    ContextInjectionMiddleware,
    ToolAllowlistMiddleware,
)
from agent_flows_builder.prompts import FLOW_BUILDER_MASTER_PROMPT
from agent_flows_builder.resources import ensure_resources_available
from agent_flows_builder.settings import AgentSettings
from agent_flows_builder.telemetry import initialize_phoenix_tracing
from agent_flows_builder.tools import update_flow_metadata, update_flow_steps
from agent_flows_builder.tools.files import create_composite_backend
from agent_flows_builder.tools.mcp_discovery import (
    configure_mcp_tools,
    get_mcp_action_schema,
    list_mcp_servers,
)
from agent_flows_builder.utils.models import create_chat_model
from agent_flows_builder.utils.workspace import set_workspace

SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"

ALLOWED_MASTER_TOOLS = {
    "read_file",
    "update_flow_steps",
    "update_flow_metadata",
    "list_mcp_servers",
    "get_mcp_action_schema",
    "task",  # Subagent launcher
    "write_todos",  # Planning tool from deepagents middleware
}


def create_flow_builder_agent(
    realtimex_ai_api_key: str,
    realtimex_ai_base_path: str,
    mcp_aci_api_key: str,
    mcp_aci_linked_account_owner_id: str,
    workspace: Path | str | None = None,
    checkpointer=None,
    settings: AgentSettings | None = None,
    local_mcp_base_url: str = "http://localhost:3001",
):
    """Create the production-ready Flow Builder Agent.

    Architecture:
    - Master agent: Handles most workflow building directly using real filesystem tools
    - Configuration reference specialist: Provides executor parameter documentation (read-only access)
    - Flow validator specialist: Validates completed workflows for correctness (validation tool access)

    The agent builds workflow configurations by:
    1. Understanding user automation requirements through natural language
    2. Delegating executor configuration research to configuration reference specialist
    3. Implementing and registering workflow steps using specialist guidance
    4. Delegating final validation to flow validator specialist
    5. Assembling complete, validated workflow configurations

    Args:
        realtimex_ai_api_key: Required API key for RealtimeX AI provider.
        realtimex_ai_base_path: Required base URL for RealtimeX AI provider.
        mcp_aci_api_key: Required API key for MCP ACI service.
        mcp_aci_linked_account_owner_id: Required linked account owner ID for MCP ACI service.
        workspace: Directory containing docs/ folder. If None, uses current working directory
                  for direct execution or creates temp workspace for package usage.
        checkpointer: Optional checkpointer for conversation persistence. If None, no persistence.
        settings: Optional override for runtime configuration. If not provided, values are
                  loaded from environment variables via AgentSettings.
        local_mcp_base_url: Base URL for local MCP servers. Defaults to http://localhost:3001.

    Configuration:
    - Models, temperature, and limits are configurable through AgentSettings
    - Environment variables are respected when settings are not supplied explicitly

    Returns:
        LangGraph agent ready for workflow automation assistance

    Raises:
        RuntimeError: If documentation is not found in the specified workspace
    """
    # Set global workspace for all file tools
    workspace = set_workspace(workspace)

    # Ensure docs and skills are available in specified workspace
    resource_info = ensure_resources_available(workspace)
    workspace = resource_info.workspace
    if not resource_info.all_available:
        missing_msg = ", ".join(resource_info.missing) if resource_info.missing else "docs, skills"  # fmt: skip
        raise RuntimeError(
            f"Critical failure: Required resources missing ({missing_msg}). "
            "The agent requires documentation to ground its responses and prevent hallucination. "
            "Ensure the agent_flows_builder package includes docs/skills or set AGENT_FLOWS_WORKSPACE "
            "to a directory containing the required resources."
        )

    # Resolve runtime settings
    agent_settings = settings or AgentSettings.from_env()

    # Configure Phoenix tracing (defaults can be overridden via environment)
    initialize_phoenix_tracing()

    # Create provider config from required parameters
    provider_config = ModelProviderConfig(
        api_key=realtimex_ai_api_key, base_path=realtimex_ai_base_path
    )

    # Configure MCP tools with credentials and optional local URL
    configure_mcp_tools(
        mcp_aci_api_key, mcp_aci_linked_account_owner_id, local_mcp_base_url
    )

    # Configure backend: state-backed scratchpad + docs/skills routed to filesystem
    skills_dir = resource_info.skills_dir
    backend_factory = lambda runtime: create_composite_backend(  # noqa: E731
        resource_info, runtime
    )

    # Create configuration expert sub-agent with provider config and read-only tools
    configuration_expert = create_configuration_expert(
        provider_config=provider_config,
        settings=agent_settings,
        backend_factory=backend_factory,
    )

    # Create flow architect sub-agent with provider config and read-only tools
    flow_architect = create_flow_architect(
        provider_config=provider_config,
        settings=agent_settings,
        backend_factory=backend_factory,
    )

    # Create flow validator specialist as custom sub-agent with validation tool
    flow_validator_specialist = create_flow_validator(
        provider_config=provider_config,
        settings=agent_settings,
        backend_factory=backend_factory,
    )

    # Create configured chat model with provider config
    chat_model = create_chat_model(
        model=agent_settings.master.model,
        provider_config=provider_config,
        temperature=agent_settings.master.temperature,
        max_tokens=agent_settings.master.max_tokens,
        parallel_tool_calls=False,
    )

    # Create master agent with filesystem and MCP discovery tools
    flow_builder_agent = create_realtimex_deep_agent(
        tools=[
            update_flow_steps,
            update_flow_metadata,
            list_mcp_servers,
            get_mcp_action_schema,
        ],  # Read-only filesystem comes from FilesystemMiddleware; explicit tools are flow manipulation + MCP discovery
        system_prompt=FLOW_BUILDER_MASTER_PROMPT,
        model=chat_model,
        subagents=[flow_architect, configuration_expert, flow_validator_specialist],
        backend=backend_factory,
        enable_skills=skills_dir.exists(),
        workspace_skills_dir="/skills/" if skills_dir.exists() else None,
        middleware=[
            ContextInjectionMiddleware(
                target_placeholders=["{{FLOW_GRAPH}}", "{{FLOW_VARIABLES}}"]
            ),
            ToolAllowlistMiddleware(ALLOWED_MASTER_TOOLS),
        ],
    ).with_config({"recursion_limit": agent_settings.recursion_limit})

    # Assign checkpointer if provided
    if checkpointer:
        flow_builder_agent.checkpointer = checkpointer

    return flow_builder_agent
