"""
Trix Python SDK - Official Python client for Trix API.

Trix is a memory and knowledge management API that provides:
- Memory storage and retrieval
- Relationship management between memories
- Clustering and organization
- Graph traversal and analysis
- Semantic search
- Webhooks for event notifications
- Agent session management

Example:
    >>> from trix import Trix
    >>> client = Trix(api_key="your_api_key")
    >>> memory = client.memories.create(content="Important information")
    >>> print(memory.id)

Async Example:
    >>> from trix import AsyncTrix
    >>> async with AsyncTrix(api_key="your_api_key") as client:
    ...     memory = await client.memories.create(content="Important information")
    ...     print(memory.id)
"""

# Version constants - must be defined before importing submodules to avoid circular imports
__version__ = "0.1.1"
__api_version__ = "v1"
MIN_API_VERSION = "v1"
MAX_API_VERSION = "v1"

# ruff: noqa: E402
from .client import (
    AsyncTrix,
    ErrorInterceptor,
    PoolConfig,
    RequestContext,
    RequestInterceptor,
    ResponseContext,
    ResponseInterceptor,
    Trix,
)
from .protocols import AsyncClientProtocol, ClientProtocol, SyncClientProtocol
from .utils.pagination import AsyncPaginator, SyncPaginator
from .utils.retry import RetryConfig
from .utils.security import (
    validate_id,
    validate_base_url,
    validate_webhook_url,
    redact_sensitive_data,
    get_env_credential,
    mask_credential,
)
from .utils.logging import (
    LogConfig,
    LogFormat,
    LogLevel,
    get_logger,
    setup_logging,
    request_context,
)
from .utils.metrics import (
    InMemoryCollector,
    MetricsCollector,
    RequestMetrics,
    get_metrics_collector,
    set_metrics_collector,
    timed_request,
)
from .utils.telemetry import (
    TelemetryConfig,
    SpanStatusCode,
    SpanKind,
    RequestSpan,
    configure_telemetry,
    get_telemetry_config,
    is_telemetry_enabled,
    create_request_span,
    traced,
    with_tracing,
    with_tracing_async,
)
from .exceptions import (
    APIError,
    APIVersionMismatchError,
    AuthenticationError,
    ConnectionError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    ServerError,
    TimeoutError,
    TrixError,
    ValidationError,
)
from .types import (
    AgentContext,
    AgentSession,
    BulkResult,
    Cluster,
    ClusterCreate,
    ClusterList,
    ClusterMembership,
    ClusterUpdate,
    ConsolidationResult,
    ConsolidationStrategy,
    Direction,
    EmbedAllResponse,
    EmbeddingResponse,
    ExtractionType,
    ExtractedHighlights,
    FeedbackResponse,
    FeedbackResult,
    FeedbackSubmit,
    GraphContext,
    GraphNode,
    GraphTraversal,
    Highlight,
    HighlightCreate,
    HighlightList,
    HighlightUpdate,
    Job,
    JobList,
    JobStats,
    JobStatus,
    Memory,
    MemoryConfig,
    MemoryCreate,
    MemoryList,
    MemoryOptions,
    MemoryType,
    MemoryUpdate,
    PaginatedResponse,
    Pagination,
    Relationship,
    RelationshipCreate,
    RelationshipList,
    RelationshipType,
    RelationshipUpdate,
    SearchConfig,
    SearchMode,
    SearchResult,
    SearchResults,
    SessionMemory,
    SessionMemoryList,
    SessionList,
    ShortestPath,
    Space,
    SpaceCreate,
    SpaceList,
    SpaceUpdate,
    Webhook,
    WebhookCreate,
    WebhookDelivery,
    WebhookDeliveryList,
    WebhookEvent,
    WebhookFilter,
    WebhookList,
    WebhookUpdate,
)

__all__ = [
    # Clients
    "Trix",
    "AsyncTrix",
    # Protocols
    "SyncClientProtocol",
    "AsyncClientProtocol",
    "ClientProtocol",
    # Utilities
    "RetryConfig",
    "PoolConfig",
    "SyncPaginator",
    "AsyncPaginator",
    # Pagination types
    "Pagination",
    "PaginatedResponse",
    "BulkResult",
    # Interceptors
    "RequestContext",
    "ResponseContext",
    "RequestInterceptor",
    "ResponseInterceptor",
    "ErrorInterceptor",
    # Security utilities
    "validate_id",
    "validate_base_url",
    "validate_webhook_url",
    "redact_sensitive_data",
    "get_env_credential",
    "mask_credential",
    # Logging utilities
    "LogConfig",
    "LogFormat",
    "LogLevel",
    "get_logger",
    "setup_logging",
    "request_context",
    # Metrics utilities
    "InMemoryCollector",
    "MetricsCollector",
    "RequestMetrics",
    "get_metrics_collector",
    "set_metrics_collector",
    "timed_request",
    # Telemetry utilities (OpenTelemetry integration)
    "TelemetryConfig",
    "SpanStatusCode",
    "SpanKind",
    "RequestSpan",
    "configure_telemetry",
    "get_telemetry_config",
    "is_telemetry_enabled",
    "create_request_span",
    "traced",
    "with_tracing",
    "with_tracing_async",
    # Exceptions
    "TrixError",
    "APIError",
    "APIVersionMismatchError",
    "AuthenticationError",
    "PermissionError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "ConnectionError",
    "TimeoutError",
    # Types - Memory
    "Memory",
    "MemoryCreate",
    "MemoryUpdate",
    "MemoryList",
    "MemoryConfig",
    "MemoryOptions",
    "MemoryType",
    # Types - Relationship
    "Relationship",
    "RelationshipCreate",
    "RelationshipUpdate",
    "RelationshipList",
    "RelationshipType",
    # Types - Cluster
    "Cluster",
    "ClusterCreate",
    "ClusterUpdate",
    "ClusterList",
    "ClusterMembership",
    # Types - Space
    "Space",
    "SpaceCreate",
    "SpaceUpdate",
    "SpaceList",
    # Types - Graph
    "GraphNode",
    "GraphTraversal",
    "GraphContext",
    "ShortestPath",
    "Direction",
    # Types - Search
    "SearchResult",
    "SearchResults",
    "SearchConfig",
    "SearchMode",
    "EmbeddingResponse",
    "EmbedAllResponse",
    # Types - Webhook
    "Webhook",
    "WebhookCreate",
    "WebhookUpdate",
    "WebhookList",
    "WebhookDelivery",
    "WebhookDeliveryList",
    "WebhookEvent",
    "WebhookFilter",
    # Types - Agent
    "AgentSession",
    "SessionMemory",
    "SessionMemoryList",
    "SessionList",
    "ConsolidationResult",
    "ConsolidationStrategy",
    "AgentContext",
    # Types - Feedback
    "FeedbackSubmit",
    "FeedbackResult",
    "FeedbackResponse",
    # Types - Highlights
    "Highlight",
    "HighlightCreate",
    "HighlightUpdate",
    "HighlightList",
    "ExtractedHighlights",
    "ExtractionType",
    # Types - Jobs
    "Job",
    "JobList",
    "JobStats",
    "JobStatus",
]
