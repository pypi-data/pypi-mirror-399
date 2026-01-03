"""
ThinkHive Python SDK
OpenTelemetry-based observability for AI agents
"""

from opentelemetry import trace
try:
    # Try to use HTTP+JSON exporter (simpler, no protobuf required)
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    EXPORTER_TYPE = "http+proto"
except ImportError:
    # Fallback to gRPC exporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    EXPORTER_TYPE = "grpc"
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
import functools
from typing import Optional, Dict, Any, Callable
import os

__version__ = "0.1.0"

# Global tracer
_tracer: Optional[trace.Tracer] = None
_initialized = False


def init(
    api_key: Optional[str] = None,
    endpoint: str = "https://thinkhivemind-h25z7pvd3q-uc.a.run.app",
    service_name: str = "my-ai-agent",
    agent_id: Optional[str] = None,
):
    """
    Initialize ThinkHive SDK with OTLP exporter

    Args:
        api_key: ThinkHive API key (or set THINKHIVE_API_KEY env var)
        endpoint: ThinkHive endpoint URL
        service_name: Name of your service/agent
        agent_id: Optional agent ID (or set THINKHIVE_AGENT_ID env var)
    """
    global _tracer, _initialized

    if _initialized:
        return

    # Get API key from env if not provided
    api_key = api_key or os.getenv("THINKHIVE_API_KEY")
    agent_id = agent_id or os.getenv("THINKHIVE_AGENT_ID")

    if not api_key and not agent_id:
        raise ValueError("Either api_key or agent_id must be provided")

    # Create resource with service name
    resource = Resource.create({
        "service.name": service_name,
    })

    # Create tracer provider
    provider = TracerProvider(resource=resource)

    # Configure OTLP exporter
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    elif agent_id:
        headers["X-Agent-ID"] = agent_id

    exporter = OTLPSpanExporter(
        endpoint=f"{endpoint}/v1/traces",
        headers=headers,
    )

    # Add span processor
    provider.add_span_processor(BatchSpanProcessor(exporter))

    # Set global tracer provider
    trace.set_tracer_provider(provider)

    # Get tracer
    _tracer = trace.get_tracer(__name__, __version__)
    _initialized = True

    print(f"✅ ThinkHive SDK initialized (endpoint: {endpoint})")


def get_tracer() -> trace.Tracer:
    """Get the global tracer instance"""
    global _tracer
    if not _initialized:
        raise RuntimeError("ThinkHive SDK not initialized. Call thinkhive.init() first.")
    return _tracer


def trace_llm(
    model_name: Optional[str] = None,
    provider: Optional[str] = None,
):
    """
    Decorator for tracing LLM calls

    Usage:
        @trace_llm(model_name="gpt-4", provider="openai")
        def call_llm(prompt):
            return openai.chat.completions.create(...)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.start_as_current_span(
                func.__name__,
                attributes={
                    "openinference.span.kind": "LLM",
                    "llm.model_name": model_name,
                    "llm.provider": provider,
                }
            ) as span:
                try:
                    result = func(*args, **kwargs)

                    # Try to extract token counts if result is OpenAI-like
                    if hasattr(result, "usage"):
                        usage = result.usage
                        if hasattr(usage, "prompt_tokens"):
                            span.set_attribute("llm.token_count.prompt", usage.prompt_tokens)
                        if hasattr(usage, "completion_tokens"):
                            span.set_attribute("llm.token_count.completion", usage.completion_tokens)
                        if hasattr(usage, "total_tokens"):
                            span.set_attribute("llm.token_count.total", usage.total_tokens)

                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        return wrapper
    return decorator


def trace_retrieval(query: Optional[str] = None):
    """
    Decorator for tracing retrieval/RAG operations

    Usage:
        @trace_retrieval()
        def search_documents(query):
            return vector_db.search(query)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.start_as_current_span(
                func.__name__,
                attributes={
                    "openinference.span.kind": "RETRIEVER",
                    "retrieval.query": query or (args[0] if args else None),
                }
            ) as span:
                try:
                    result = func(*args, **kwargs)

                    # If result is a list of documents, record them
                    if isinstance(result, list) and len(result) > 0:
                        for i, doc in enumerate(result[:10]):  # Limit to first 10
                            if hasattr(doc, "id"):
                                span.set_attribute(f"retrieval.documents.{i}.document.id", doc.id)
                            if hasattr(doc, "score"):
                                span.set_attribute(f"retrieval.documents.{i}.document.score", doc.score)
                            if hasattr(doc, "content"):
                                content = doc.content[:500]  # Truncate
                                span.set_attribute(f"retrieval.documents.{i}.document.content", content)

                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        return wrapper
    return decorator


def trace_tool(tool_name: Optional[str] = None):
    """
    Decorator for tracing tool/function calls

    Usage:
        @trace_tool(tool_name="web_search")
        def search_web(query):
            return requests.get(f"https://api.example.com/search?q={query}")
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.start_as_current_span(
                tool_name or func.__name__,
                attributes={
                    "openinference.span.kind": "TOOL",
                    "tool.name": tool_name or func.__name__,
                }
            ) as span:
                try:
                    result = func(*args, **kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        return wrapper
    return decorator


__all__ = [
    "init",
    "get_tracer",
    "trace_llm",
    "trace_retrieval",
    "trace_tool",
]
