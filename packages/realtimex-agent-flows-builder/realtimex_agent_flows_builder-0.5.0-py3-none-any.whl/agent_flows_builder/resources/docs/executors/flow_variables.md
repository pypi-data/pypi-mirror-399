# Flow Variables Executor

- **Type**: `flow_variables`
- **Purpose**: Central registry for workflow data (user inputs, defaults, downstream outputs)
- **Position**: Must be the first block in every flow

---

## Overview

The Flow Variables executor declares every variable that a workflow can read or update. Use it to capture user inputs, seed system configuration, and pre-register the result variables that later executors will populate. Any reference to `{{ $variable_name }}` elsewhere in the flow must correspond to an entry defined here.

---

## Configuration Schema

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `variables` | `array` | No | `[]` | List of variable definitions to initialize or reserve.

### Variable Definition Schema

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `name` | `string` | **Yes** | | Variable name (must be a valid Python identifier).
| `type` | `string` | **Yes** | | One of `string`, `number`, `boolean`, `array`, `object`, `null`.
| `value` | `any` | No | `null` | Initial value; must match `type` when provided.
| `description` | `string` | No | `""` | Short context to help AI-driven steps understand usage.
| `source` | `string` | No | `user_input` | Data origin: `user_input`, `node_output`, or `system`.

---

## Variable Sources

- **`user_input`** – Values collected from the user before execution begins.
- **`node_output`** – Placeholders that downstream executors will populate.
- **`system`** – Static defaults or environment configuration.

---

## Canonical Examples

### 1. Declare Inputs, Defaults, and Result Placeholders
```json
{
  "type": "flow_variables",
  "config": {
    "variables": [
      {
        "name": "search_topic",
        "type": "string",
        "source": "user_input",
        "description": "Topic the user wants to research"
      },
      {
        "name": "api_base_url",
        "type": "string",
        "value": "https://api.example.com",
        "source": "system"
      },
      {
        "name": "summary_text",
        "type": "string",
        "value": null,
        "source": "node_output",
        "description": "LLM generated summary"
      }
    ]
  }
}
```

### 2. Flow Variables Paired with a Downstream Step
```json
[
  {
    "type": "flow_variables",
    "config": {
      "variables": [
        {"name": "user_id", "type": "string", "source": "user_input"},
        {"name": "api_url", "type": "string", "value": "https://api.example.com", "source": "system"},
        {"name": "user_data", "type": "object", "value": null, "source": "node_output"}
      ]
    }
  },
  {
    "type": "apiCall",
    "config": {
      "url": "{{ $api_url }}/users/{{ $user_id }}",
      "method": "GET",
      "responseVariable": "user_data"
    }
  }
]
```

---

## Variable Interpolation

```json
{
  "type": "flow_variables",
  "config": {
    "variables": [
      {"name": "base_url", "type": "string", "value": "https://api.example.com", "source": "system"},
      {"name": "version", "type": "string", "value": "v1", "source": "system"}
    ]
  }
}
```

Later steps can safely reference `{{ $base_url }}/{{ $version }}/users` and use dot notation for nested access such as `{{ $api_response.data.status }}`.

---

## Variable Naming Rules

- Use valid Python identifiers (`user_id`, `_session_token`, `MAX_RETRIES`).
- Avoid spaces, hyphens, or reserved keywords (`class`, `for`).
- Keep names consistent with the workflow's domain terminology.

---

## Error Handling & Best Practices

- Deduplicate variable names; duplicates cause validation failures.
- Match the `type` to the stored value or to the expected structure of downstream outputs.
- Only declare variables that the workflow actually needs to keep initialization lean.
- Use the `description` field to clarify semantic meaning for AI-powered steps.
