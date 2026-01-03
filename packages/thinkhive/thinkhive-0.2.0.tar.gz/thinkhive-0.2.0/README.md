# ThinkHive Python SDK

OpenTelemetry-based observability SDK for AI agents supporting 25 trace formats including LangSmith, Langfuse, Opik, Braintrust, Datadog, MLflow, and more.

## Installation

```bash
pip install thinkhive
```

## Quick Start

```python
import thinkhive

# Initialize SDK
thinkhive.init(
    api_key="your-api-key",  # or set THINKHIVE_API_KEY
    service_name="my-ai-agent"
)

# Trace LLM calls
@thinkhive.trace_llm(model_name="gpt-4", provider="openai")
def call_llm(prompt):
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response

# Trace retrieval operations
@thinkhive.trace_retrieval()
def search_documents(query):
    results = vector_db.search(query)
    return results

# Trace tool calls
@thinkhive.trace_tool(tool_name="web_search")
def search_web(query):
    return requests.get(f"https://api.example.com/search?q={query}")
```

## Environment Variables

- `THINKHIVE_API_KEY`: Your ThinkHive API key
- `THINKHIVE_AGENT_ID`: Your agent ID (alternative to API key)

## License

MIT
