"""Flow operations utility functions."""

import copy
import re
from typing import Any

from jsonpath_ng.ext import parse as jsonpath_parse


def normalize_jsonpath(path: str) -> str:
    """Corrects JSONPath strings for properties like 'truePath'."""
    # This regex finds .truePath or .falsePath and converts to ['truePath'] etc.
    return re.sub(r"\.(true|false)(Path)", r"['\1\2']", path)


def collect_all_step_ids(steps: list[dict], ids: set[str] | None = None) -> set[str]:
    """Recursively collect all step IDs from flow, including nested structures."""
    if ids is None:
        ids = set()

    for step in steps:
        if "id" in step:
            ids.add(step["id"])

        # Check nested structures
        config = step.get("config", {})

        # Conditional: truePath, falsePath
        if "truePath" in config and isinstance(config["truePath"], list):
            collect_all_step_ids(config["truePath"], ids)
        if "falsePath" in config and isinstance(config["falsePath"], list):
            collect_all_step_ids(config["falsePath"], ids)

        # Switch: cases[].blocks and defaultBlocks
        if "cases" in config and isinstance(config["cases"], list):
            for case in config["cases"]:
                if "blocks" in case and isinstance(case["blocks"], list):
                    collect_all_step_ids(case["blocks"], ids)
        if "defaultBlocks" in config and isinstance(config["defaultBlocks"], list):
            collect_all_step_ids(config["defaultBlocks"], ids)

        # Loop: loopBlocks
        if "loopBlocks" in config and isinstance(config["loopBlocks"], list):
            collect_all_step_ids(config["loopBlocks"], ids)

    return ids


def find_step_by_id(
    steps: list[dict], step_id: str, path: list[Any] | None = None
) -> tuple[dict | None, list[Any]]:
    """
    Find step by ID recursively, returning (step, path_to_parent_array).

    path_to_parent_array is a list of (container, key) tuples to navigate back.
    """
    if path is None:
        path = []

    for idx, step in enumerate(steps):
        if step.get("id") == step_id:
            return step, path + [(steps, idx)]

        # Check nested structures
        config = step.get("config", {})

        # Conditional: truePath, falsePath
        for branch in ["truePath", "falsePath"]:
            if branch in config and isinstance(config[branch], list):
                found, found_path = find_step_by_id(
                    config[branch], step_id, path + [(config, branch)]
                )
                if found:
                    return found, found_path

        # Switch: cases[...].blocks and defaultBlocks
        if "cases" in config and isinstance(config["cases"], list):
            for case_idx, case in enumerate(config["cases"]):
                if "blocks" in case and isinstance(case["blocks"], list):
                    found, found_path = find_step_by_id(
                        case["blocks"],
                        step_id,
                        path + [(config["cases"], case_idx), (case, "blocks")],
                    )
                    if found:
                        return found, found_path

        if "defaultBlocks" in config and isinstance(config["defaultBlocks"], list):
            found, found_path = find_step_by_id(
                config["defaultBlocks"], step_id, path + [(config, "defaultBlocks")]
            )
            if found:
                return found, found_path

        # Loop: loopBlocks
        if "loopBlocks" in config and isinstance(config["loopBlocks"], list):
            found, found_path = find_step_by_id(
                config["loopBlocks"], step_id, path + [(config, "loopBlocks")]
            )
            if found:
                return found, found_path

    return None, []


def find_step_id_by_type(flow: dict[str, Any], step_type: str) -> str | None:
    """Return the id of the first step matching step_type, or None if not found."""
    for step in flow.get("steps", []):
        if step.get("type") == step_type:
            return step.get("id")
    return None


def resolve_target_array(flow: dict, path: str | None) -> tuple[list[dict] | None, str]:
    """Resolve path to target step array, or return root steps."""
    if not path:
        return flow.get("steps", []), ""

    try:
        normalized_path = normalize_jsonpath(path)
        jsonpath_expr = jsonpath_parse(normalized_path)
        matches = jsonpath_expr.find(flow)

        if not matches:
            return None, f"JSONPath '{path}' did not match any location in flow"

        if len(matches) > 1:
            return (
                None,
                f"JSONPath '{path}' matched multiple locations. Use more specific path.",
            )

        target_array = matches[0].value

        if not isinstance(target_array, list):
            return None, f"JSONPath '{path}' must resolve to an array/list"

        return target_array, ""

    except Exception as e:
        return None, f"Invalid JSONPath '{path}': {str(e)}"


def validate_step_structure(step: dict) -> tuple[bool, str]:
    """Validate that a step contains all required keys."""
    required_keys = ["id", "type", "config"]
    for key in required_keys:
        if key not in step:
            return False, f"Step missing required '{key}' field"
    return True, ""


def validate_variable_structure(variable: dict) -> tuple[bool, str]:
    """Validate that a variable contains all required keys."""
    required_keys = ["name", "type"]
    for key in required_keys:
        if key not in variable:
            return False, f"Variable missing required '{key}' field"
    return True, ""


def deep_merge(base: dict, update: dict) -> dict:
    """Deep merge update dict into base dict, preserving unspecified fields."""
    result = copy.deepcopy(base)
    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result
