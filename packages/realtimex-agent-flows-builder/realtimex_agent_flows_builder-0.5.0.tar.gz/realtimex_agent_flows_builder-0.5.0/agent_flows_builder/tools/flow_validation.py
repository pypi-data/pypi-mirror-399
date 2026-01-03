"""Flow validation tool for Agent Flows Builder."""

import asyncio
import json

from agent_flows import AgentFlowsConfig, FlowConfig, FlowExecutor
from langchain.tools import ToolRuntime, tool
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from agent_flows_builder.utils.file_operations import load_flow_json


def _transform_validation_result(raw_result: dict) -> dict:
    """Transform package output to agent-consumable format."""
    issues = []
    for step_summary in raw_result.get("step_validation_summary", []):
        if not step_summary.get("valid"):
            for message in step_summary.get("messages", []):
                issues.append(
                    {
                        "type": "error",
                        "message": message,
                        "step_id": step_summary.get("step_id"),
                    }
                )

    return {"is_valid": raw_result.get("valid", False), "issues": issues}


@tool
def validate_flow_configuration(
    runtime: ToolRuntime,
) -> Command:
    """Validate /flow.json configuration for structural correctness and variable consistency.

    Args:
        runtime: Tool runtime injected by LangChain

    Returns:
        Command with validation results in agent-consumable JSON format
    """
    target_path = "/flow.json"
    mock_filesystem = runtime.state.get("files", {})
    if target_path not in mock_filesystem:
        error_result = {
            "is_valid": False,
            "issues": [
                {
                    "type": "error",
                    "message": f"Flow file '{target_path}' not found",
                    "step_id": None,
                }
            ],
        }
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=json.dumps(error_result),
                        tool_call_id=runtime.tool_call_id,
                    )
                ],
            }
        )

    flow_content = mock_filesystem[target_path]

    try:
        # Parse and load the flow definition
        flow_definition = load_flow_json(flow_content)
        flow_config = FlowConfig(**flow_definition)

        # Initialize the executor with a dummy API key (not required for JSON validation)
        executor = FlowExecutor(
            config=AgentFlowsConfig(
                api_key="__DUMMY_API_KEY__",
            )
        )

        # Validate the flow
        validation_result_raw = asyncio.run(
            executor.validate_flow(flow_source=flow_config)
        )

        # Transform to agent-consumable format
        agent_result = _transform_validation_result(validation_result_raw)

        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=json.dumps(agent_result),
                        tool_call_id=runtime.tool_call_id,
                    )
                ],
            }
        )

    except (json.JSONDecodeError, ValueError, TypeError) as e:
        error_result = {
            "is_valid": False,
            "issues": [
                {
                    "type": "error",
                    "message": f"Invalid JSON format: {str(e)}",
                    "step_id": None,
                }
            ],
        }
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=json.dumps(error_result),
                        tool_call_id=runtime.tool_call_id,
                    )
                ],
            }
        )

    except Exception as e:
        error_result = {
            "is_valid": False,
            "issues": [
                {
                    "type": "error",
                    "message": f"Flow validation failed: {str(e)}",
                    "step_id": None,
                }
            ],
        }
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=json.dumps(error_result),
                        tool_call_id=runtime.tool_call_id,
                    )
                ],
            }
        )
