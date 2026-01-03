# Switch Executor

**Type**: `switch`
**Purpose**: Execute different blocks of steps by matching a variable against a set of predefined cases.

---

## Configuration Schema

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `variable` | `string` | **Yes** | | The variable to evaluate, using `{{ $variable }}` syntax. Supports dot notation for nested access (e.g., `{{ $user.profile.role }}`). |
| `cases` | `array` | **Yes** | | An array of case objects to match against. See schema below. |
| `defaultBlocks` | `array` | No | `[]` | An array of steps to execute if no case value matches the variable. |

---

## Case Object Schema

Each object in the `cases` array defines a single branch of logic.

| Field | Type | Required | Description |
|---|---|---|---|
| `value` | `any` | **Yes** | The specific value to match against the `variable`. The first case with an exact match will be executed. |
| `blocks` | `array` | **Yes** | The array of steps to execute if this case matches. |

---

## Output Variable

The `switch` executor **does not produce its own output variable**. Any variables produced by steps within a `case` or `defaultBlocks` must be pre-declared in the `flow_variables` executor (Flow Variables step) as per the standard variable management protocol.

---

## Canonical Example

### Routing Based on User Role

This demonstrates routing the workflow to different API calls based on the user's role, with a fallback for unknown roles. This is the primary and most common use case.

```json
{
  "type": "switch",
  "config": {
    "variable": "{{ $user.role }}",
    "cases": [
      {
        "value": "admin",
        "blocks": [
          {
            "id": "fetch_admin_data",
            "type": "apiCall",
            "config": {
              "url": "https://api.example.com/admin/dashboard",
              "responseVariable": "dashboard_data"
            }
          }
        ]
      },
      {
        "value": "user",
        "blocks": [
          {
            "id": "fetch_user_data",
            "type": "apiCall",
            "config": {
              "url": "https://api.example.com/users/dashboard",
              "responseVariable": "dashboard_data"
            }
          }
        ]
      }
    ],
    "defaultBlocks": [
      {
        "id": "handle_guest_user",
        "type": "llmInstruction",
        "config": {
          "instruction": "The user is a guest. Generate a generic welcome message.",
          "resultVariable": "welcome_message"
        }
      }
    ]
  }
}
```