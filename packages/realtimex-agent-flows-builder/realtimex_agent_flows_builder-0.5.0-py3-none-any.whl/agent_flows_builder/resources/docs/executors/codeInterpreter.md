# Code Interpreter Executor

**Type**: `codeInterpreter`  
**Purpose**: Execute lightweight Python scripts and return the `result` payload into your flow.

## Configuration
All fields are optional except `script.code` (required) and `runtime.language` (defaults to `"python"`).

| Field | Type | Default | Description |
|---|---|---|---|
| `runtime.language` | enum | `"python"` | Interpreter runtime (Python only). |
| `runtime.version` | string\|null | `null` | Optional version hint. |
| `runtime.dependencies` | list\<string> | `[]` | Optional package requirements; empty strings are invalid. |
| `script.kind` | literal `"inline"` | `"inline"` | Script source type. |
| `script.code` | string | — | Python source to execute; use ONLY `{{ $variable }}` for interpolation; AVOID filters like `\| tojson`. |
| `resultVariable` | string\|null | `null` | Flow variable to store the interpreter’s `result`. |
| `timeout` | integer | `0` | Request timeout in seconds (`0` disables). |
| `maxRetries` | integer | `0` | Retry attempts for transport errors. |

## Output Mapping (important)
To populate `resultVariable`, print your payload inside `<output>` tags:
```python
print("<output>{output_data}</output>")
```
- The executor extracts whatever is inside `<output>…</output>` and assigns it to `resultVariable`.
- If the content parses as JSON/dict, `resultVariable` becomes a dict; otherwise it is stored as a string (tags removed).

## Examples
**With dependencies and result variable**
```json
{
  "type": "codeInterpreter",
  "config": {
    "runtime": {
      "language": "python",
      "dependencies": ["requests"]
    },
    "script": {
      "kind": "inline",
      "code": "import requests, json\nresp = requests.get('https://jsonplaceholder.typicode.com/users/2').json()\nprint('<output>' + json.dumps(resp) + '</output>')"
    },
    "resultVariable": "user_payload",
    "maxRetries": 2,
    "timeout": 30
  }
}
```

## Notes for agents
- Always fetch the current schema before using this executor; never guess fields.
- Register `resultVariable` in Flow Variables when set.
- Keep scripts short; use dependencies sparingly.
