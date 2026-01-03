# Finish Executor (Proposed)
- **Type**: `finish`
- **Purpose**: Terminate the flow; optional simple UI output. Works with empty config.

## Config (all optional)
| Field | Default | Notes |
|---|---|---|
| `flowAsOutput` | `false` | If true, return only the flow result. |
| `useLLM` | `false` | LLM formatting for UI output. |
| `inputData` | `""` | Input text when `useLLM` is true. |
| `uiComponents` | `null` | Simple UI payload: `type: "responseData"`, `dataType: "text"|"markdown"`, `data: { "content": "<text or {{ $var }}>" }`. |

## Behavior
- Always emits a finish signal; runs with empty config.
- `flowAsOutput: true` → output flow result only.
- With `uiComponents`: render text/markdown; `useLLM`/`inputData` control formatting.

## Examples (compact but clear)
- Minimal
```json
{ "type": "finish", "config": {} }
```
- Flow result only
```json
{ "type": "finish", "config": { "flowAsOutput": true } }
```
- UI output (choose dataType)
```json
{
  "type": "finish",
  "config": {
    "flowAsOutput": true,
    "uiComponents": {
      "type": "responseData",
      "dataType": "text",          // or "markdown"
      "data": { "content": "{{ $api_response }}" } // or "## Summary\n\n{{ $summary }}"
    }
  }
}
```

## Notes
- Keep configs minimal; all fields optional.
- Do not add result variables unless explicitly needed elsewhere.
- If unsure about output style (text vs markdown, LLM formatting), ask the user.
