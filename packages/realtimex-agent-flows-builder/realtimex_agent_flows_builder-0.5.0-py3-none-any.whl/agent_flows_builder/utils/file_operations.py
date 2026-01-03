"""Shared file operation utilities to eliminate code duplication."""

import json

from deepagents.backends.utils import create_file_data

DEFAULT_LINE_LIMIT = 2000
MAX_LINE_LENGTH = 2000


def format_file_lines_with_numbers(
    content: str, offset: int = 0, limit: int = DEFAULT_LINE_LIMIT
) -> str:
    """Format file content with line numbers (cat -n format) applying offset/limit.

    Args:
        content: Raw file content
        offset: Starting line number (0-based)
        limit: Maximum number of lines to return

    Returns:
        Formatted string with line numbers, or error message if offset too large
    """
    if not content or content.strip() == "":
        return "System reminder: File exists but has empty contents"

    lines = content.splitlines()
    start_idx = offset
    end_idx = min(start_idx + limit, len(lines))

    if start_idx >= len(lines):
        return f"Error: Line offset {offset} exceeds file length ({len(lines)} lines)"

    result_lines = []
    for i in range(start_idx, end_idx):
        line_content = lines[i]
        # Truncate overly long lines
        if len(line_content) > MAX_LINE_LENGTH:
            line_content = line_content[:MAX_LINE_LENGTH]
        line_number = i + 1
        result_lines.append(f"{line_number:6d}\t{line_content}")

    return "\n".join(result_lines)


def validate_and_replace_string(
    content: str, old_string: str, new_string: str, replace_all: bool = False
) -> tuple[str, str]:
    """Validate string replacement and perform it, returning new content and success message.

    Args:
        content: Original file content
        old_string: String to find and replace
        new_string: Replacement string
        replace_all: Whether to replace all occurrences

    Returns:
        Tuple of (new_content, success_message) or raises formatted error string
    """
    if old_string not in content:
        raise ValueError(f"Error: String not found in file: '{old_string}'")

    # Check for multiple occurrences if not replacing all
    if not replace_all:
        occurrences = content.count(old_string)
        if occurrences > 1:
            raise ValueError(
                f"Error: String '{old_string}' appears {occurrences} times in file. "
                f"Use replace_all=True to replace all instances, or provide a more "
                f"specific string with surrounding context."
            )

    # Perform replacement
    if replace_all:
        new_content = content.replace(old_string, new_string)
        replacement_count = content.count(old_string)
        result_msg = (
            f"Successfully replaced {replacement_count} instance(s) of the string"
        )
    else:
        new_content = content.replace(old_string, new_string, 1)
        result_msg = "Successfully replaced string"

    return new_content, result_msg


def load_flow_json(flow_content: str | list[str] | dict) -> dict:
    """Load flow JSON from various formats.

    Handles multiple formats:
    1. JSON string: '{"name": "flow", ...}'
    2. List of lines: ['{', '  "name": "flow",', ...']
    3. FileData dict: {"content": [...lines...], "created_at": "...", "modified_at": "..."}
    4. Already parsed flow dict: {"name": "flow", ...}

    Args:
        flow_content: Flow content in any supported format

    Returns:
        Parsed flow dictionary

    Raises:
        json.JSONDecodeError: If the content is not valid JSON
        TypeError: If the content type is not supported
    """
    # If dict, check if it's FileData format or flow dict
    if isinstance(flow_content, dict):
        # Check if it's FileData format (has 'content' key)
        if "content" in flow_content:
            # Extract content lines from FileData
            content_lines = flow_content["content"]
            if isinstance(content_lines, list):
                flow_content = "\n".join(content_lines)
            else:
                flow_content = content_lines
        else:
            # Already a flow dict, return as-is
            return flow_content

    # If list of strings (lines), join them
    if isinstance(flow_content, list):
        if not flow_content:
            raise ValueError("Empty list provided for flow content")
        if not all(isinstance(line, str) for line in flow_content):
            raise TypeError("List must contain only strings")
        flow_content = "\n".join(flow_content)

    # If string, parse it
    if isinstance(flow_content, str):
        return json.loads(flow_content)

    raise TypeError(
        f"Unsupported flow content type: {type(flow_content).__name__}. "
        "Expected str, list[str], or dict"
    )


def save_flow_json(flow: dict) -> dict:
    """Save flow dictionary to FileData format.

    Args:
        flow: Flow dictionary to serialize

    Returns:
        FileData dict with content (as lines), created_at, and modified_at
    """
    json_string = json.dumps(flow, ensure_ascii=False, indent=2)
    return create_file_data(json_string)
