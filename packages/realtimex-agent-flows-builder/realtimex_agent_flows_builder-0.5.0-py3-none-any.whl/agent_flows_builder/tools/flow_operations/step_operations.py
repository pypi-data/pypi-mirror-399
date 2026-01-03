from agent_flows_builder.tools.flow_operations.utils import (
    collect_all_step_ids,
    deep_merge,
    find_step_by_id,
    resolve_target_array,
    validate_step_structure,
)


def add_step(
    flow: dict,
    step: dict,
    target_id: str | None,
    position: str | None,
    path: str | None,
) -> tuple[dict, str, bool]:
    """Add step with global ID validation."""
    # Validate step structure
    valid, error = validate_step_structure(step)
    if not valid:
        return flow, f"Error: {error}", False

    # Global duplicate check
    all_step_ids = collect_all_step_ids(flow.get("steps", []))
    if step["id"] in all_step_ids:
        return (
            flow,
            f"Error: Step with id '{step['id']}' already exists (checked globally including nested steps). Use update_step to modify or choose a different id.",
            False,
        )

    # Resolve target array
    target_array, error = resolve_target_array(flow, path)
    if error:
        return flow, f"Error: {error}", False

    # Determine insertion index
    if position and target_id:
        target_idx = None
        for idx, s in enumerate(target_array):
            if s.get("id") == target_id:
                target_idx = idx
                break

        if target_idx is None:
            return (
                flow,
                f"Error: Target step '{target_id}' not found in target array",
                False,
            )

        insert_idx = target_idx if position == "before" else target_idx + 1
        target_array.insert(insert_idx, step)
        location = f"{position} '{target_id}'"
    else:
        # Default: before finish
        finish_idx = None
        for idx, s in enumerate(target_array):
            if s.get("id") == "finish":
                finish_idx = idx
                break

        if finish_idx is not None:
            target_array.insert(finish_idx, step)
            location = "before finish"
        else:
            target_array.append(step)
            location = "at end of steps"

    path_desc = f" in nested path: {path}" if path else ""
    return flow, f"Added step '{step['id']}' {location}{path_desc}", True


def update_step(
    flow: dict, target_id: str, update_data: dict, path: str | None
) -> tuple[dict, str, bool]:
    """Update step with deep merge, supporting nested paths."""
    if path:
        # Navigate to nested array first, then find step
        target_array, error = resolve_target_array(flow, path)
        if error:
            return flow, f"Error: {error}", False

        target_idx = None
        for idx, step in enumerate(target_array):
            if step.get("id") == target_id:
                target_idx = idx
                break

        if target_idx is None:
            return flow, f"Error: Step '{target_id}' not found in path '{path}'", False

        target_array[target_idx] = deep_merge(target_array[target_idx], update_data)
        return flow, f"Updated step '{target_id}' in path '{path}'", True
    else:
        # Global search
        step_ref, step_path = find_step_by_id(flow.get("steps", []), target_id)

        if not step_ref:
            return flow, f"Error: Step '{target_id}' not found", False

        # Navigate to parent and update
        if step_path:
            container, key = step_path[-1]
            if isinstance(key, int):
                container[key] = deep_merge(container[key], update_data)
            else:
                container[key] = deep_merge(container[key], update_data)

        return flow, f"Updated step '{target_id}'", True


def remove_step(flow: dict, target_id: str, path: str | None) -> tuple[dict, str, bool]:
    """Remove step with protection for critical steps, supporting nested paths."""
    # Protect critical steps
    if target_id in ["flow_variables", "finish"]:
        return flow, f"Error: Cannot remove required step '{target_id}'", False

    if path:
        # Navigate to nested array first
        target_array, error = resolve_target_array(flow, path)
        if error:
            return flow, f"Error: {error}", False

        target_idx = None
        for idx, step in enumerate(target_array):
            if step.get("id") == target_id:
                target_idx = idx
                break

        if target_idx is None:
            return flow, f"Error: Step '{target_id}' not found in path '{path}'", False

        target_array.pop(target_idx)
        return flow, f"Removed step '{target_id}' from path '{path}'", True
    else:
        # Global search
        step_ref, step_path = find_step_by_id(flow.get("steps", []), target_id)

        if not step_ref:
            return flow, f"Error: Step '{target_id}' not found", False

        # Navigate to parent and remove
        if step_path:
            container, key = step_path[-1]
            if isinstance(container, list) and isinstance(key, int):
                container.pop(key)

        return flow, f"Removed step '{target_id}'", True
