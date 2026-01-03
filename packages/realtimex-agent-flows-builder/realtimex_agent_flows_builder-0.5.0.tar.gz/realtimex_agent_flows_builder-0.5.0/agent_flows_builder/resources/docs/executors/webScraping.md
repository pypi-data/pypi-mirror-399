# Web Scraping Executor

**Type**: `webScraping`
**Purpose**: Extract and process content from web pages using various modes, including AI-powered analysis.

---

## Configuration Schema

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `urls` | `array` | **Yes** | | An array of one or more URL strings to scrape. |
| `extraction` | `object` | **Yes** | | The extraction configuration object. See modes below. |
| `browser` | `object` | No | `{}` | Browser settings (e.g., `headless`, `userAgent`). |
| `page` | `object` | No | `{}` | Page interaction settings (e.g., `waitFor`, `timeoutMs`). |
| `retry` | `object` | No | `{}` | Retry settings (e.g., `attempts`). |
| `resultVariable` | `string` | No | `null` | The variable to store the array of scraping results. |
| `directOutput` | `boolean` | No | `false` | If `true`, returns results directly instead of storing in a variable. |

---

## Extraction Modes

The `extraction.mode` field determines the scraping strategy.

| Mode | Description |
|---|---|
| `markdown` | Extracts the main content of the page as clean markdown. |
| `html` | Extracts the HTML of the page. Use `extraction.htmlVariant: "clean" | "raw"`. |
| `schema` | Extracts structured data based on a defined schema of CSS selectors. |
| `llm` | Uses an LLM to analyze the page content and extract information based on an instruction. |

---

### Extraction Mode: `schema`

When `mode` is `schema`, the `extraction.schema` object is required.

| Field | Type | Required | Description |
|---|---|---|---|
| `baseSelector` | `string` | **Yes** | The CSS selector for the parent element of each item to be extracted. |
| `fields` | `array` | **Yes** | An array of field objects to define the data to extract from each parent. |

**Field Object Schema:**
| Field | Type | Required | Description |
|---|---|---|---|
| `name` | `string` | **Yes** | The key for the extracted data in the final JSON object. |
| `selector` | `string` | **Yes** | The CSS selector for the element within the `baseSelector`. |
| `type` | `string` | **Yes** | The type of extraction. Valid: `text`, `attribute`. |
| `attribute`| `string` | If `type: "attribute"` | The name of the HTML attribute to extract (e.g., `href`, `src`). |

---

### Extraction Mode: `llm`

When `mode` is `llm`, the `extraction.llm` object is required. This uses the same configuration as the `llmInstruction` executor.

| Field | Type | Required | Description |
|---|---|---|---|
| `instruction` | `string` | **Yes** | The prompt for the LLM to perform on the page content. |
| `provider` | `string` | No | LLM provider (e.g., `openai`, `anthropic`, `ollama`). |
| `model` | `string` | No | The specific model to use. |
| `responseFormat`| `string` | No | The expected format. Valid: `text`, `json`. Default: `json`. |

---

## Output Variable (`resultVariable`)

When `resultVariable` is set, it stores an `object` containing a `results` key, which is an `array`. Each element in the array is an object corresponding to a scraped URL.

**Output Structure:**
```json
{
  "results": [
    {
      "url": "https://example.com/page1",
      "success": true,
      "content": "..." // Type depends on extraction mode
    },
    {
      "url": "https://example.com/page2",
      "success": false,
      "error": "HTTP 404: Not Found"
    }
  ]
}
```
The `content` field's type depends on the `extraction.mode`:
- `markdown` / `html`: `string`
- `schema`: `array` of `object`s
- `llm`: `string` or `object`/`array` (based on `responseFormat`)

---

## Canonical Examples

### 1. Markdown Extraction

This demonstrates extracting the main content of a blog post as clean markdown.

```json
{
  "type": "webScraping",
  "config": {
    "urls": ["{{ $blog_post_url }}"],
    "extraction": {
      "mode": "markdown"
    },
    "resultVariable": "article_markdown"
  }
}
```

### 2. Structured Data Extraction (`schema`)

This demonstrates extracting product information from an e-commerce page.

```json
{
  "type": "webScraping",
  "config": {
    "urls": ["{{ $product_listing_url }}"],
    "extraction": {
      "mode": "schema",
      "schema": {
        "baseSelector": ".product-card",
        "fields": [
          { "name": "product_name", "selector": "h2.product-title", "type": "text" },
          { "name": "price", "selector": ".price-tag", "type": "text" },
          { "name": "link", "selector": "a.product-link", "type": "attribute", "attribute": "href" }
        ]
      }
    },
    "resultVariable": "product_data"
  }
}
```

### 3. AI-Powered Extraction (`llm`)

This demonstrates using an LLM to analyze a news article and extract key information as JSON.

```json
{
  "type": "webScraping",
  "config": {
    "urls": ["{{ $news_article_url }}"],
    "extraction": {
      "mode": "llm",
      "llm": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "instruction": "Extract the author, publication date, and a 3-sentence summary from this article.",
        "responseFormat": "json"
      }
    },
    "resultVariable": "article_summary"
  }
}
```