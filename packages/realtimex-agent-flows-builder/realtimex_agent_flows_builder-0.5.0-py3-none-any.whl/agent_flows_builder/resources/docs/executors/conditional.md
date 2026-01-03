# Conditional Executor

**Type**: `conditional`
**Purpose**: Execute different blocks of steps based on the evaluation of a condition.

---

## Configuration Schema

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `condition` | `object` | **Yes** | | The condition object to evaluate. See schema below. |
| `truePath` | `array` | No | `[]` | An array of steps to execute if the condition is `true`. |
| `falsePath` | `array` | No | `[]` | An array of steps to execute if the condition is `false`. |

---

## Condition Object Schema

The `condition` object controls how comparisons are grouped and evaluated.

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `combinator` | `string` | No | `"and"` | Logical operator applied to `conditions`. Accepts `and`, `or`, or `not`. |
| `conditions` | `array` | **Yes** | | Ordered list of condition clauses or nested groups to evaluate. |

Each entry in `conditions` is either:
- A nested condition group with its own `combinator` and `conditions`, or
- A terminal clause with the fields below.

If `conditions` contains a single clause, you may omit `combinator`; it defaults to `"and"`. Use `"not"` with a single clause or group to invert the result.

| Clause Field | Type | Required | Description |
|---|---|---|---|
| `variable` | `string` | **Yes** | Variable path to evaluate, wrapped in interpolation syntax (e.g., `"{{ $api_response.status }}"`). Dot notation is supported inside the braces. |
| `operator` | `string` | **Yes** | Comparison operator. See Supported Operators. |
| `value` | `any` | **No** | Value to compare against. Supports string interpolation (`"{{ $variable_name }}"`). Omit for `is_empty` / `is_not_empty`. |

---

## Supported Operators

| Operator | Type(s) | Description |
|---|---|---|
| `equals` | `any` | Checks for exact equality (`==`). |
| `not_equals` | `any` | Checks for inequality (`!=`). |
| `greater_than` | `number` | Checks if `variable` > `value`. |
| `less_than` | `number` | Checks if `variable` < `value`. |
| `greater_than_or_equal` | `number` | Checks if `variable` >= `value`. |
| `less_than_or_equal` | `number` | Checks if `variable` <= `value`. |
| `contains` | `string` | Checks if `variable` contains the `value` substring. |
| `not_contains` | `string` | Checks if `variable` does not contain the `value` substring. |
| `starts_with` | `string` | Checks if `variable` starts with the `value` string. |
| `ends_with` | `string` | Checks if `variable` ends with the `value` string. |
| `is_empty` | `any` | Checks if `variable` is `null`, `""`, `[]`, or `{}`. The `value` field is ignored. |
| `is_not_empty` | `any` | Checks if `variable` is not empty. The `value` field is ignored. |

---

## Output Variable

The `conditional` executor **does not produce its own output variable**. Any variables produced by steps within the `truePath` or `falsePath` must be pre-declared in the `flow_variables` executor (Flow Variables step) as per the standard variable management protocol.

---

## Canonical Examples

These examples serve as the primary structural blueprints for the agent.

### 1. Basic Routing Based on a String Value

Routes execution based on a status string captured earlier in the flow.

```json
{
  "type": "conditional",
  "config": {
    "condition": {
      "conditions": [
        {
          "variable": "{{ $api_response.status }}",
          "operator": "equals",
          "value": "completed"
        }
      ]
    },
    "truePath": [
      {
        "id": "send_success_email",
        "type": "mcpServerAction",
        "config": { ... }
      }
    ],
    "falsePath": [
      {
        "id": "log_failed_status",
        "type": "llmInstruction",
        "config": { ... }
      }
    ]
  }
}
```

### 2. Body Content Check for Error Handling

Combines checks on both HTTP status and payload to decide on an error path.

```json
{
  "type": "conditional",
  "config": {
    "condition": {
      "combinator": "and",
      "conditions": [
        {
          "variable": "{{ $api_response.http_code }}",
          "operator": "equals",
          "value": 200
        },
        {
          "combinator": "or",
          "conditions": [
            {
              "variable": "{{ $api_response.body.status }}",
              "operator": "equals",
              "value": "error"
            },
            {
              "variable": "{{ $api_response.body.message }}",
              "operator": "contains",
              "value": "retry"
            }
          ]
        }
      ]
    },
    "truePath": [
      {
        "id": "handle_api_error",
        "type": "llmInstruction",
        "config": {
          "instruction": "An API error occurred. The message was: {{ $api_response.message }}. Log this issue."
        }
      }
    ],
    "falsePath": []
  }
}
```