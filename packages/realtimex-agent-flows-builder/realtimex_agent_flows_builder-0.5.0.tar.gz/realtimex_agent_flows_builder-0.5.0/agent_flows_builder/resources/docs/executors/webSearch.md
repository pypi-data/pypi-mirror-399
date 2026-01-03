# Web Search Executor

- **Type**: `webSearch`
- **Purpose**: Execute web searches and retrieve structured results from various search providers.

---

## Configuration Schema

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `query` | `string` | **Yes** | | Search query string. Supports variable interpolation. |
| `provider` | `object` | **Yes** | | Search provider configuration with name and config. |
| `maxResults` | `integer` | No | `10` | Maximum number of results to return (1-100). |
| `searchType` | `string` | No | `"search"` | Type of search. Valid: `"search"`, `"news"`. |
| `resultVariable` | `string` | No | `null` | Variable to store the search results object. |
| `directOutput` | `boolean` | No | `false` | If `true`, returns results directly instead of storing in a variable. |
| `timeout` | `integer` | No | `30` | Request timeout in seconds. |
| `maxRetries` | `integer` | No | `3` | Maximum retry attempts on failure (0-10). |

### Provider Configuration

The `provider` field requires:

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | `string` | **Yes** | Provider identifier: `"google"`, `"bing"`, `"duckduckgo"`, `"serpapi"`, `"serply"`, `"searxng"`, `"tavily"`. |
| `config` | `object` | **Yes** | Provider-specific configuration (API keys, endpoints, etc.). |
| `fallbacks` | `array` | No | Array of fallback providers with same structure as main provider. |

#### Provider-Specific Config Requirements

- **`google`**: `apiKey` (string), `searchEngineId` (string)
- **`bing`**: `apiKey` (string)
- **`serpapi`**: `apiKey` (string)
- **`serply`**: `apiKey` (string)
- **`searxng`**: `baseUrl` (string)
- **`tavily`**: `apiKey` (string)
- **`duckduckgo`**: No configuration required

---

## Output Variable (`resultVariable`)

When `resultVariable` is set, it stores a comprehensive search results object.

The output variable type is always `object`, containing:
- Search metadata (provider, query, total results count)
- Results array with title, URL, snippet, and metadata for each result
- Related searches and search metadata

---

## Canonical Examples

These examples serve as the primary structural blueprints for the agent.

### 1. Basic Google Search

This demonstrates a simple search operation with a single provider.

```json
{
  "type": "webSearch",
  "config": {
    "query": "{{ $search_topic }} latest trends",
    "provider": {
      "name": "google",
      "config": {
        "apiKey": "{{ $google_api_key }}",
        "searchEngineId": "{{ $google_cse_id }}"
      }
    },
    "maxResults": 10,
    "resultVariable": "search_results"
  }
}
```

### 2. Complex Multi-Provider with Fallbacks

This demonstrates provider fallback mechanism and news search type.

```json
{
  "type": "webSearch",
  "config": {
    "query": "{{ $company_name }} {{ $event_type }} news",
    "provider": {
      "name": "serpapi",
      "config": {
        "apiKey": "{{ $serpapi_key }}"
      },
      "fallbacks": [
        {
          "name": "bing",
          "config": {
            "apiKey": "{{ $bing_api_key }}"
          }
        },
        {
          "name": "duckduckgo",
          "config": {}
        }
      ]
    },
    "searchType": "news",
    "maxResults": 20,
    "resultVariable": "news_results",
    "maxRetries": 2
  }
}
```