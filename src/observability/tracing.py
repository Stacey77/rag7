"""Distributed tracing with OpenTelemetry."""
from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Global tracer instance
_tracer: Optional[trace.Tracer] = None


def init_tracing(
    service_name: str = "rag7-agent-api",
    jaeger_endpoint: str = "http://localhost:14268/api/traces",
) -> trace.Tracer:
    """Initialize OpenTelemetry tracing with OTLP exporter.
    
    Note: For Jaeger, use the OTLP endpoint (default: localhost:4317)
    or configure Jaeger to expose OTLP gRPC endpoint.
    
    Args:
        service_name: Name of the service
        jaeger_endpoint: Jaeger/OTLP collector endpoint
        
    Returns:
        Configured tracer instance
    """
    global _tracer

    # Create a resource with service name
    resource = Resource(attributes={SERVICE_NAME: service_name})

    # Create OTLP exporter (more modern and widely supported)
    # Note: Jaeger supports OTLP natively
    otlp_endpoint = jaeger_endpoint.replace("/api/traces", "").replace("14268", "4317")
    otlp_exporter = OTLPSpanExporter(
        endpoint=otlp_endpoint,
        insecure=True,  # Use False in production with proper TLS
    )

    # Create a TracerProvider
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(processor)

    # Set the global tracer provider
    trace.set_tracer_provider(provider)

    # Get a tracer
    _tracer = trace.get_tracer(__name__)

    return _tracer


def get_tracer() -> trace.Tracer:
    """Get the configured tracer instance.
    
    Returns:
        Tracer instance
        
    Raises:
        RuntimeError: If tracing has not been initialized
    """
    if _tracer is None:
        raise RuntimeError("Tracing not initialized. Call init_tracing() first.")
    return _tracer


def trace_agent_conversation(agent_name: str, task_id: str):
    """Context manager for tracing agent conversations.
    
    Args:
        agent_name: Name of the agent
        task_id: Unique task identifier
        
    Usage:
        with trace_agent_conversation("research_agent", "task-123"):
            # Agent work here
            pass
    """
    tracer = get_tracer()
    return tracer.start_as_current_span(
        f"agent.{agent_name}",
        attributes={
            "agent.name": agent_name,
            "task.id": task_id,
        },
    )


def trace_llm_call(model: str, provider: str):
    """Context manager for tracing LLM API calls.
    
    Args:
        model: Model name
        provider: Provider name (e.g., openai, anthropic)
        
    Usage:
        with trace_llm_call("gpt-4", "openai"):
            # LLM call here
            pass
    """
    tracer = get_tracer()
    return tracer.start_as_current_span(
        f"llm.{provider}.{model}",
        attributes={
            "llm.model": model,
            "llm.provider": provider,
        },
    )


def add_span_attribute(key: str, value: str) -> None:
    """Add an attribute to the current span.
    
    Args:
        key: Attribute key
        value: Attribute value
    """
    span = trace.get_current_span()
    if span:
        span.set_attribute(key, value)


def add_span_event(name: str, attributes: Optional[dict] = None) -> None:
    """Add an event to the current span.
    
    Args:
        name: Event name
        attributes: Optional event attributes
    """
    span = trace.get_current_span()
    if span:
        span.add_event(name, attributes=attributes or {})
