# MCP Server Action Executor

**Type**: `mcpServerAction`
**Purpose**: Execute actions on external tools and services via the Model Context Protocol (MCP).

---

## Configuration Schema

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `provider` | `string` | **Yes** | | MCP provider type. Valid: `remote`, `local`. |
| `serverId` | `string` | **Yes** | | The unique identifier for the target MCP server (e.g., `GMAIL`). |
| `action` | `string` | **Yes** | | The specific action/tool name to execute on the server (e.g., `GMAIL__SEND_EMAIL`). |
| `params` | `object` | No | `{}` | A key-value object of parameters to pass to the action. Supports interpolation. |
| `resultVariable` | `string` | No | `null` | The variable to store the action's response. |
| `directOutput` | `boolean` | No | `false` | If `true`, returns response directly instead of storing in a variable. |
| `timeout` | `integer` | No | `60` | Request timeout in seconds (1-300). |
| `maxRetries`| `integer` | No | `2` | Maximum retry attempts for server/network errors (0-10). |

---

## Important Note on Dynamic Behavior

The available `serverId`, `action`, and `params` are **dynamic and depend on the user's specific MCP setup.** They are not a fixed list.

A dedicated sub-agent with specialized tools will be available in the future to discover and configure MCP actions. For now, the `Configuration Reference Specialist` should assume the Master Agent will provide the necessary `serverId` and `action` based on user context.

---

## Output Variable (`resultVariable`)

When `resultVariable` is set, it stores the direct response from the MCP action. The data type of this variable (`string`, `object`, `array`, etc.) is **determined by the specific MCP action being called.** The agent must be prepared to handle various output structures.

---

## Canonical Example

### Sending a Gmail Email

This example demonstrates a common use case of interacting with a remote MCP server to perform an action (sending an email). The specific `serverId`, `action`, and `params` are determined by the MCP Gmail tool's definition.

```json
{
  "type": "mcpServerAction",
  "config": {
    "provider": "remote",
    "serverId": "GMAIL",
    "action": "GMAIL__SEND_EMAIL",
    "params": {
      "recipient": "{{ $recipient_email }}",
      "subject": "Update on your request",
      "body": "{{ $email_body_content }}"
    },
    "resultVariable": "email_send_status"
  }
}
```