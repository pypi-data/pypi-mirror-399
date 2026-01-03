# API Call Executor

- **Type**: `apiCall`
- **Purpose**: Execute HTTP requests to external APIs and web services.

---

## Configuration Schema

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `url` | `string` | **Yes** | | Request URL. Must start with `http://` or `https://`. |
| `method` | `string` | No | `GET` | HTTP method. Valid: `GET`, `POST`, `PUT`, `DELETE`, `PATCH`, `HEAD`, `OPTIONS`. |
| `headers` | `array` | No | `[]` | Array of key-value objects for request headers. |
| `bodyType` | `string` | No | `null` | Request body type. Required for POST/PUT/PATCH. Valid: `json`, `form`, `text`, `raw`. |
| `body` | `string` | No | `null` | Request body content. Used for `bodyType: json | text | raw`. Supports interpolation. |
| `formData` | `array` | No | `[]` | Array of key-value objects. Used for `bodyType: form`. |
| `resultVariable` | `string` | No | `null` | Variable to store the response body. |
| `directOutput` | `boolean` | No | `false` | If `true`, returns response directly instead of storing in a variable. |
| `timeout` | `integer` | No | `30` | Request timeout in seconds (1-300). |
| `maxRetries`| `integer` | No | `0` | Maximum retry attempts for server/network errors (0-10). |
| `followRedirects` | `boolean` | No | `true` | Automatically follow HTTP redirects. |

---

## Output Variable (`resultVariable`)

When `resultVariable` is set, it stores **only the parsed body** of the API response. It does not include status codes or headers.

The data type of this variable depends on the API response's `Content-Type` header:
- `application/json`: The output will be an `object` or `array`.
- `text/plain`, `text/html`, etc.: The output will be a `string`.

---

## Canonical Examples

These examples serve as the primary structural blueprints for the agent.

### 1. Basic GET Request

This demonstrates a simple data retrieval operation, storing the result in a variable.

```json
{
  "type": "apiCall",
  "config": {
    "url": "https://api.example.com/users/{{ $user_id }}",
    "method": "GET",
    "resultVariable": "user_data",
    "timeout": 30
  }
}
```

### 2. Complex POST with JSON Body and Headers

This demonstrates a resource creation operation, showing headers, a JSON body with interpolated variables, and retry logic.

```json
{
  "type": "apiCall",
  "config": {
    "url": "https://api.example.com/v1/messages",
    "method": "POST",
    "headers": [
      { "key": "Content-Type", "value": "application/json" },
      { "key": "Authorization", "value": "Bearer {{ $api_token }}" }
    ],
    "bodyType": "json",
    "body": "{\"recipient\": \"{{ $recipient_email }}\", \"message\": \"{{ $message_content }}\"}",
    "resultVariable": "send_message_result",
    "maxRetries": 3
  }
}
```