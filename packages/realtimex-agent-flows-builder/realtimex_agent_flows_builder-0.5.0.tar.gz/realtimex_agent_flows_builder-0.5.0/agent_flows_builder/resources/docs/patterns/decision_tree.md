# Flow Pattern: Decision Tree

**Use Case**: Complex branching logic where a single `conditional` (if/else) is insufficient.
**Examples**:
- "If user is VIP, send email; if Free, show ad; if Enterprise, alert sales."
- "Route support tickets based on priority (High, Medium, Low)."

## Architectural Blueprint

1.  **Input Evaluation**: Identify the variable that determines the path (e.g., `{{ $user_tier }}`).
2.  **Switch Node**: Use a `switch` executor to define cases.
3.  **Branch Execution**: Each case triggers a distinct sequence of steps.

## Configuration Rules

### 1. Switch Configuration
- **Variable**: The variable to evaluate.
- **Cases**: An **Array** of objects, each with `value` and `blocks`.
- **Default**: `defaultBlocks` for fallback if no case matches.

### 2. Branch Definition
- Define separate steps for each branch within the `blocks` array.
- Ensure all branches eventually converge or terminate cleanly.

## Example Structure

```json
[
  {
    "type": "switch",
    "config": {
      "variable": "{{ $priority }}",
      "cases": [
        {
          "value": "HIGH",
          "blocks": [
            {
              "id": "branch_high",
              "type": "apiCall",
              "config": { ... } // Alert Ops Team
            }
          ]
        },
        {
          "value": "MEDIUM",
          "blocks": [
            {
              "id": "branch_medium",
              "type": "apiCall",
              "config": { ... } // Create Ticket
            }
          ]
        }
      ],
      "defaultBlocks": [
        {
          "id": "branch_low",
          "type": "apiCall",
          "config": { ... } // Log info
        }
      ]
    }
  }
]
```
