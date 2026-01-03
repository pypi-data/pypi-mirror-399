from agent_flows_builder.tools.flow_operations.utils import (
    deep_merge,
    validate_variable_structure,
)


def add_variables(flow: dict, variables: list[dict]) -> tuple[dict, str, bool]:
    """Add variables to flow_variables step with strict duplicate checking."""
    # Find flow_variables step
    flow_vars_step = None
    for step in flow.get("steps", []):
        if step.get("type") == "flow_variables":
            flow_vars_step = step
            break

    if not flow_vars_step:
        return flow, "Error: flow_variables step not found in flow", False

    # Validate all variables
    for var in variables:
        valid, error = validate_variable_structure(var)
        if not valid:
            return flow, f"Error: {error}", False

    # Get existing variables
    existing_vars = flow_vars_step.get("config", {}).get("variables", [])
    existing_names = {v["name"] for v in existing_vars}

    # Check for duplicates (strict)
    for var in variables:
        if var["name"] in existing_names:
            return (
                flow,
                f"Error: Variable '{var['name']}' already exists. Use update_variables to modify or remove_variables to delete it first.",
                False,
            )

    # Add new variables
    flow_vars_step.setdefault("config", {}).setdefault("variables", []).extend(
        variables
    )
    var_names = ", ".join(v["name"] for v in variables)
    return flow, f"Added {len(variables)} variable(s): {var_names}", True


def update_variables(flow: dict, updates: list[dict]) -> tuple[dict, str, bool]:
    """Update existing variables in flow_variables step."""
    # Find flow_variables step
    flow_vars_step = None
    for step in flow.get("steps", []):
        if step.get("type") == "flow_variables":
            flow_vars_step = step
            break

    if not flow_vars_step:
        return flow, "Error: flow_variables step not found in flow", False

    # Validate all updates have name field
    for update in updates:
        if "name" not in update:
            return flow, "Error: Each variable update must have 'name' field", False

    existing_vars = flow_vars_step.get("config", {}).get("variables", [])

    updated_count = 0
    for update in updates:
        var_name = update["name"]
        found = False

        for idx, var in enumerate(existing_vars):
            if var["name"] == var_name:
                # Deep merge update into existing variable
                existing_vars[idx] = deep_merge(var, update)
                found = True
                updated_count += 1
                break

        if not found:
            return (
                flow,
                f"Error: Variable '{var_name}' not found. Use add_variables to create it first.",
                False,
            )

    var_names = ", ".join(u["name"] for u in updates)
    return flow, f"Updated {updated_count} variable(s): {var_names}", True


def remove_variables(flow: dict, var_names: list[str | dict]) -> tuple[dict, str, bool]:
    """Remove variables from flow_variables step."""
    # Find flow_variables step
    flow_vars_step = None
    for step in flow.get("steps", []):
        if step.get("type") == "flow_variables":
            flow_vars_step = step
            break

    if not flow_vars_step:
        return flow, "Error: flow_variables step not found in flow", False

    # Normalize to list of strings
    names_to_remove = []
    for item in var_names:
        if isinstance(item, str):
            names_to_remove.append(item)
        elif isinstance(item, dict) and "name" in item:
            names_to_remove.append(item["name"])
        else:
            return (
                flow,
                "Error: remove_variables data must be list of strings or dicts with 'name' field",
                False,
            )

    existing_vars = flow_vars_step.get("config", {}).get("variables", [])

    # Remove variables
    removed_names = []
    for name in names_to_remove:
        found = False
        for idx, var in enumerate(existing_vars):
            if var["name"] == name:
                existing_vars.pop(idx)
                removed_names.append(name)
                found = True
                break

        if not found:
            return flow, f"Error: Variable '{name}' not found", False

    if removed_names:
        names_str = ", ".join(removed_names)
        return flow, f"Removed {len(removed_names)} variable(s): {names_str}", True
    else:
        return flow, "No variables removed", True
