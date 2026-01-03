"""LangChain tool definitions for flow manipulation."""

import json
from typing import Literal

from langchain.tools import ToolRuntime, tool
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from agent_flows_builder.tools.flow_operations.step_operations import (
    add_step,
    remove_step,
    update_step,
)
from agent_flows_builder.tools.flow_operations.utils import find_step_id_by_type
from agent_flows_builder.tools.flow_operations.variable_operations import (
    add_variables,
    remove_variables,
    update_variables,
)
from agent_flows_builder.utils.file_operations import load_flow_json, save_flow_json


@tool(parse_docstring=True)
def update_flow_steps(  # noqa: PLR0915
    runtime: ToolRuntime,
    operation: Literal[
        "add_variables",
        "update_variables",
        "remove_variables",
        "add_step",
        "update_step",
        "remove_step",
    ],
    data: dict | list[dict] | None = None,
    target_id: str | None = None,
    position: Literal["before", "after"] | None = None,
    path: str | None = None,
) -> Command:
    """Manipulates flow steps and variables using semantic operations.

    This tool handles all step-related and variable-related modifications to /flow.json.
    Use `update_flow_metadata` tool for name/description changes.

    Operations:

    1. add_variables: Add variable definitions to `flow_variables`
       Required: data (list of variable defs)
       Example: data=[{"name": "x", "type": "string", ...}]

    2. update_variables: Update existing variable definitions
       Required: data (list of variable updates with "name" field)
       Example: data=[{"name": "x", "type": "number", "description": "Updated"}]

    3. remove_variables: Remove variables by name
       Required: data (list of dicts with "name" field)
       Example: data=[{"name": "var1"}, {"name": "var2"}]

    4. add_step: Insert step at specified location
       Required: data (step config dict)
       Optional: target_id + position (for relative positioning)
       Optional: path (for nested insertion via JSONPath)
       Example: data={"id": "fetch", "type": "apiCall", "config": {...}}

    5. update_step: Modify existing step (deep merge)
       Required: target_id, data (partial step config)
       Optional: path (to locate step in nested structure)
       Example: target_id="fetch", data={"config": {"url": "https://new.com"}}

    6. remove_step: Remove step by ID
       Required: target_id
       Optional: path (to locate step in nested structure)
       Example: target_id="old_step"

    Args:
        runtime: Injected ToolRuntime (state/context) provided by LangGraph; not visible to the model.
        operation (str): Type of modification
        data (dict | list): Content to add/update (varies by operation)
        target_id (str, optional): Step ID to target (for update_step, remove_step, relative add_step)
        position (str, optional): "before" or "after" for relative add_step positioning
        path (str, optional): JSONPath for nested operations (e.g., "$.steps[?(@.id=='x')].config['truePath']")
    """
    # Get flow from state
    files = runtime.state.get("files", {})
    if "/flow.json" not in files:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content="Error: /flow.json not found in state",
                        tool_call_id=runtime.tool_call_id,
                    )
                ]
            }
        )

    try:
        flow = load_flow_json(files["/flow.json"])
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Error: Invalid JSON in /flow.json: {str(e)}",
                        tool_call_id=runtime.tool_call_id,
                    )
                ]
            }
        )

    # Route to operation handlers
    success = False
    message = ""

    if operation == "add_variables":
        if not isinstance(data, list):
            message = "Error: data must be a list for add_variables operation"
        else:
            flow, message, success = add_variables(flow, data)

    elif operation == "update_variables":
        if not isinstance(data, list):
            message = "Error: data must be a list for update_variables operation"
        else:
            flow, message, success = update_variables(flow, data)

    elif operation == "remove_variables":
        if not isinstance(data, list):
            message = "Error: data must be a list for remove_variables operation"
        else:
            flow, message, success = remove_variables(flow, data)

    elif operation == "add_step":
        if not isinstance(data, dict):
            message = "Error: data must be a dict for add_step operation"
        else:
            step_type = data.get("type")
            if step_type in {"finish", "flow_variables"}:
                existing_id = find_step_id_by_type(flow, step_type)
                if existing_id:
                    message = (
                        f"Step of type '{step_type}' already exists (id: '{existing_id}'). "
                        "Update the existing step instead of adding another."
                    )
                    success = False
                else:
                    flow, message, success = add_step(
                        flow, data, target_id, position, path
                    )
            else:
                flow, message, success = add_step(flow, data, target_id, position, path)

    elif operation == "update_step":
        if not target_id:
            message = "Error: target_id required for update_step operation"
        elif not isinstance(data, dict):
            message = "Error: data must be a dict for update_step operation"
        else:
            flow, message, success = update_step(flow, target_id, data, path)

    elif operation == "remove_step":
        if not target_id:
            message = "Error: target_id required for remove_step operation"
        else:
            # data is unused for remove_step; allow it to be omitted
            flow, message, success = remove_step(flow, target_id, path)

    else:
        message = f"Error: Unknown operation '{operation}'"

    # Update state if successful
    if success:
        files["/flow.json"] = save_flow_json(flow)
        return Command(
            update={
                "files": files,
                "messages": [
                    ToolMessage(content=message, tool_call_id=runtime.tool_call_id)
                ],
            }
        )
    else:
        return Command(
            update={
                "messages": [
                    ToolMessage(content=message, tool_call_id=runtime.tool_call_id)
                ]
            }
        )


@tool(parse_docstring=True)
def update_flow_metadata(
    runtime: ToolRuntime,
    name: str | None = None,
    description: str | None = None,
) -> Command:
    """Updates the name and description of the workflow.

    This tool modifies top-level metadata fields only. For all structural
    changes, such as adding or removing steps and variables, use the
    `update_flow_steps` tool.

    Args:
        runtime: Injected ToolRuntime (state/context) provided by LangGraph; not visible to the model.
        name (str, optional): The new name for the workflow.
        description (str, optional): The new description for the workflow.

    Returns:
        Command: An object containing the updated flow state or a structured
            error message if neither parameter is provided.
    """
    # Get flow from state
    files = runtime.state.get("files", {})
    if "/flow.json" not in files:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content="Error: /flow.json not found in state",
                        tool_call_id=runtime.tool_call_id,
                    )
                ]
            }
        )

    # Validate at least one parameter provided
    if name is None and description is None:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content="Error: At least one of 'name' or 'description' must be provided",
                        tool_call_id=runtime.tool_call_id,
                    )
                ]
            }
        )

    try:
        flow = load_flow_json(files["/flow.json"])
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Error: Invalid JSON in /flow.json: {str(e)}",
                        tool_call_id=runtime.tool_call_id,
                    )
                ]
            }
        )

    # Update metadata
    updated_fields = []

    if name is not None:
        flow["name"] = name
        updated_fields.append("name")

    if description is not None:
        flow["description"] = description
        updated_fields.append("description")

    # Save back to state
    files["/flow.json"] = save_flow_json(flow)

    fields_str = " and ".join(updated_fields)
    message = f"Updated flow {fields_str}"

    return Command(
        update={
            "files": files,
            "messages": [
                ToolMessage(content=message, tool_call_id=runtime.tool_call_id)
            ],
        }
    )
