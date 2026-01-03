"""Flow State formatters for system prompt injection.

This module provides functions to generate human-readable flow state
representations that can be injected into system prompts via placeholders.

Supported Placeholders:
    {{FLOW_STATE}}      - Compact combined state (variables + steps)
    {{FLOW_VARIABLES}}  - Variable registry with types and sources
    {{FLOW_STEP_IDS}}   - List of step IDs
    {{FLOW_GRAPH}}      - Visual hierarchy of steps
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class FlowConfig:
    """Input contract for all formatters.

    Attributes:
        uuid: Flow unique identifier.
        name: Flow display name.
        variables: List of variable definitions.
        steps: List of step configurations.
    """

    uuid: str
    name: str
    variables: list[dict[str, Any]]
    steps: list[dict[str, Any]]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FlowConfig:
        """Create FlowConfig from flow.json dictionary."""
        return cls(
            uuid=data.get("uuid", ""),
            name=data.get("name", "Unnamed flow"),
            variables=data.get("variables", []),
            steps=data.get("steps", []),
        )


def format_flow_variables(flow: FlowConfig) -> str:
    """Format variables for prompt injection.

    Returns:
        **Variables (N)**: `var1` (type, source), `var2` (type, source), ...
    """
    if not flow.variables:
        return "**Variables**: None defined"

    var_parts = []
    for var in flow.variables:
        name = var.get("name", "?")
        var_type = var.get("type", "any")
        source = var.get("source", "?")
        var_parts.append(f"`{name}` ({var_type}, {source})")

    return f"**Variables ({len(flow.variables)})**: {', '.join(var_parts)}"


def format_step_ids(flow: FlowConfig) -> str:
    """Format step IDs for prompt injection.

    Returns:
        **Steps**: [step_1, step_2, step_3]
    """
    if not flow.steps:
        return "**Steps**: None"

    ids = [step.get("id", "?") for step in flow.steps]
    return f"**Steps**: [{', '.join(ids)}]"


def _build_graph_lines(
    steps: list[dict[str, Any]], prefix: str = "", is_last: bool = True
) -> list[str]:
    """Recursively build graph lines for steps with nesting."""
    lines = []

    for i, step in enumerate(steps):
        step_id = step.get("id", "?")
        step_type = step.get("type", "?")
        is_step_last = i == len(steps) - 1

        # Choose connector
        if prefix == "":
            connector = ""
            child_prefix = ""
        else:
            connector = "└─ " if is_step_last else "├─ "
            child_prefix = prefix + ("   " if is_step_last else "│  ")

        # Add step line
        lines.append(f"{prefix}{connector}{step_id} ({step_type})")

        # Handle nested structures
        config = step.get("config", {})

        # Loop blocks
        if step_type == "loop" and "loopBlocks" in config:
            nested = config.get("loopBlocks", [])
            if nested:
                lines.extend(_build_graph_lines(nested, child_prefix, True))

        # Conditional paths
        elif step_type == "conditional":
            true_path = config.get("truePath", [])
            false_path = config.get("falsePath", [])

            if true_path:
                lines.append(f"{child_prefix}├─ [true]")
                lines.extend(_build_graph_lines(true_path, child_prefix + "│  ", False))
            if false_path:
                lines.append(f"{child_prefix}└─ [false]")
                lines.extend(_build_graph_lines(false_path, child_prefix + "   ", True))

        # Switch cases
        elif step_type == "switch":
            cases = config.get("cases", [])
            for j, case in enumerate(cases):
                is_case_last = j == len(cases) - 1
                case_label = case.get("value", f"case_{j}")
                case_steps = case.get("steps", [])

                case_connector = "└─ " if is_case_last else "├─ "
                lines.append(f"{child_prefix}{case_connector}[{case_label}]")

                if case_steps:
                    case_prefix = child_prefix + ("   " if is_case_last else "│  ")
                    lines.extend(_build_graph_lines(case_steps, case_prefix, True))

    return lines


def format_flow_graph(flow: FlowConfig) -> str:
    """Format visual flow graph for prompt injection.

    Returns:
        **Flow Graph**:
        ├─ flow_variables (flow_variables)
        ├─ fetch_data (apiCall)
        ├─ process_loop (loop)
        │  └─ analyze_item (llmInstruction)
        └─ finish (finish)
    """
    if not flow.steps:
        return "**Flow Graph**: Empty flow"

    lines = ["**Flow Graph** (step_id (executor_type)):"]
    total_steps = len(flow.steps)

    for i, step in enumerate(flow.steps):
        step_id = step.get("id", "?")
        step_type = step.get("type", "?")
        is_last = i == total_steps - 1

        # Use tree connectors for top-level steps
        connector = "└─" if is_last else "├─"
        lines.append(f"{connector} {step_id} ({step_type})")

        # Child prefix for nested items
        child_prefix = "   " if is_last else "│  "

        # Handle nested structures
        config = step.get("config", {})

        if step_type == "loop" and "loopBlocks" in config:
            nested = config.get("loopBlocks", [])
            if nested:
                lines.extend(_build_graph_lines(nested, child_prefix, True))

        elif step_type == "conditional":
            true_path = config.get("truePath", [])
            false_path = config.get("falsePath", [])
            if true_path:
                lines.append(f"{child_prefix}├─ [true]")
                lines.extend(_build_graph_lines(true_path, child_prefix + "│  ", False))
            if false_path:
                lines.append(f"{child_prefix}└─ [false]")
                lines.extend(_build_graph_lines(false_path, child_prefix + "   ", True))

        elif step_type == "switch":
            cases = config.get("cases", [])
            for j, case in enumerate(cases):
                is_case_last = j == len(cases) - 1
                case_label = case.get("value", f"case_{j}")
                case_connector = "└─" if is_case_last else "├─"
                lines.append(f"{child_prefix}{case_connector} [{case_label}]")
                case_steps = case.get("steps", [])
                if case_steps:
                    case_prefix = child_prefix + ("   " if is_case_last else "│  ")
                    lines.extend(_build_graph_lines(case_steps, case_prefix, True))

    return "\n".join(lines)


def format_flow_state(flow: FlowConfig) -> str:
    """Combined compact state for general use.

    Returns:
        **Variables (N)**: `var1` (type), `var2` (type), ...
        **Steps**: step1 → step2 → step3
    """
    # Variables line (compact - no source)
    if flow.variables:
        var_parts = [
            f"`{v.get('name', '?')}` ({v.get('type', 'any')})" for v in flow.variables
        ]
        vars_line = f"**Variables ({len(flow.variables)})**: {', '.join(var_parts)}"
    else:
        vars_line = "**Variables**: None defined"

    # Steps line (arrow format)
    if flow.steps:
        ids = [step.get("id", "?") for step in flow.steps]
        steps_line = f"**Steps**: {' → '.join(ids)}"
    else:
        steps_line = "**Steps**: None"

    return f"{vars_line}\n{steps_line}"


# Placeholder registry
PLACEHOLDER_REGISTRY: dict[str, callable] = {
    "{{FLOW_STATE}}": format_flow_state,
    "{{FLOW_VARIABLES}}": format_flow_variables,
    "{{FLOW_STEP_IDS}}": format_step_ids,
    "{{FLOW_GRAPH}}": format_flow_graph,
}


def inject_flow_state(
    prompt: str,
    flow: FlowConfig | dict[str, Any],
    placeholders: list[str] | None = None,
) -> str:
    """Replace placeholders in prompt with formatted state.

    Args:
        prompt: System prompt containing placeholders.
        flow: Flow configuration (FlowConfig or dict).
        placeholders: Specific placeholders to replace (default: all found).

    Returns:
        Prompt with placeholders replaced by formatted state.
    """
    # Convert dict to FlowConfig if needed
    if isinstance(flow, dict):
        flow = FlowConfig.from_dict(flow)

    # Replace each placeholder
    for placeholder, formatter in PLACEHOLDER_REGISTRY.items():
        if placeholders is None or placeholder in placeholders:
            if placeholder in prompt:
                prompt = prompt.replace(placeholder, formatter(flow))

    return prompt
