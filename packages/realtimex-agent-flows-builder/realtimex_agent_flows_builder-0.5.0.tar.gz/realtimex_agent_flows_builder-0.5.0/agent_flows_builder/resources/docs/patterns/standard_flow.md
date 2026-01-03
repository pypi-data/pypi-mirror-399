# Flow Pattern: Standard Linear Flow

**Intent**: Execute a sequence of steps one after another without complex branching or iteration.

## When to Use
- Simple "Do A, then B, then C" requests.
- No explicit mention of "for each" (Loop) or "if/else" (Conditional).

## Architectural Blueprint

1.  **Input**: Define Flow Variables for user input.
2.  **Process**: Sequence of executors (API, LLM, etc.).
3.  **Output**: Final step produces the desired result.

## Critical Configuration Rules

- **Dependency Chain**: Ensure step B uses the output of step A via `{{ $variable }}`.
- **Variable Registration**: Every step's output MUST be registered in Flow Variables.

## Example Structure

```json
[
  {
    "id": "get_input",
    "type": "flow_variables",
    "config": { ... }
  },
  {
    "id": "step_1",
    "type": "apiCall",
    "config": { "resultVariable": "step_1_result" }
  },
  {
    "id": "step_2",
    "type": "llmInstruction",
    "config": { "input": "{{ $step_1_result }}" }
  }
]
```
