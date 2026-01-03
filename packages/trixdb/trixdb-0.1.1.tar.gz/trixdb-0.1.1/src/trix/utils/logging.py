"""Structured logging utilities for Trix SDK."""

from __future__ import annotations

import json
import logging
import sys
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Iterator, MutableMapping, Optional, Tuple, Union

# Context variable for request ID tracking
_request_id: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class LogLevel(str, Enum):
    """Log levels for Trix SDK."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(str, Enum):
    """Log output formats."""

    TEXT = "text"
    JSON = "json"


@dataclass
class LogConfig:
    """Configuration for Trix logging.

    Attributes:
        level: Minimum log level to output
        format: Output format (text or json)
        include_timestamp: Whether to include timestamps
        include_request_id: Whether to include request IDs
        redact_sensitive: Whether to redact sensitive data
        logger_name: Name for the logger instance

    Example:
        >>> config = LogConfig(
        ...     level=LogLevel.DEBUG,
        ...     format=LogFormat.JSON,
        ...     include_request_id=True
        ... )
        >>> setup_logging(config)
    """

    level: LogLevel = LogLevel.INFO
    format: LogFormat = LogFormat.TEXT
    include_timestamp: bool = True
    include_request_id: bool = True
    redact_sensitive: bool = True
    logger_name: str = "trix"
    stream: Any = field(default_factory=lambda: sys.stderr)


class JsonFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def __init__(
        self,
        include_timestamp: bool = True,
        include_request_id: bool = True,
        redact_sensitive: bool = True,
    ) -> None:
        super().__init__()
        self.include_timestamp = include_timestamp
        self.include_request_id = include_request_id
        self.redact_sensitive = redact_sensitive

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if self.include_timestamp:
            log_data["timestamp"] = datetime.now(timezone.utc).isoformat()

        if self.include_request_id:
            request_id = _request_id.get()
            if request_id:
                log_data["request_id"] = request_id

        # Add extra fields
        if hasattr(record, "extra"):
            extra = record.extra
            if self.redact_sensitive:
                from .security import redact_sensitive_data

                extra = redact_sensitive_data(extra)
            log_data["extra"] = extra

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
            }

        return json.dumps(log_data, default=str)


class TextFormatter(logging.Formatter):
    """Text log formatter with optional request ID."""

    def __init__(
        self,
        include_timestamp: bool = True,
        include_request_id: bool = True,
    ) -> None:
        if include_timestamp:
            fmt = "%(asctime)s - %(name)s - %(levelname)s"
        else:
            fmt = "%(name)s - %(levelname)s"

        super().__init__(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S")
        self.include_request_id = include_request_id

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as text."""
        result = super().format(record)

        if self.include_request_id:
            request_id = _request_id.get()
            if request_id:
                result += f" [req:{request_id[:8]}]"

        result += f" - {record.getMessage()}"

        if record.exc_info:
            result += f"\n{self.formatException(record.exc_info)}"

        return result


def setup_logging(config: Optional[LogConfig] = None) -> logging.Logger:
    """Set up logging with the specified configuration.

    Args:
        config: Logging configuration. Defaults to INFO level with text format.

    Returns:
        Configured logger instance.

    Example:
        >>> from trix.utils.logging import setup_logging, LogConfig, LogLevel
        >>> logger = setup_logging(LogConfig(level=LogLevel.DEBUG))
        >>> logger.debug("Debug message")
    """
    if config is None:
        config = LogConfig()

    # Get or create logger
    logger = logging.getLogger(config.logger_name)
    logger.setLevel(getattr(logging, config.level.value))

    # Remove existing handlers
    logger.handlers.clear()

    # Create handler
    handler = logging.StreamHandler(config.stream)
    handler.setLevel(getattr(logging, config.level.value))

    # Set formatter
    if config.format == LogFormat.JSON:
        formatter: Union[JsonFormatter, TextFormatter] = JsonFormatter(
            include_timestamp=config.include_timestamp,
            include_request_id=config.include_request_id,
            redact_sensitive=config.redact_sensitive,
        )
    else:
        formatter = TextFormatter(
            include_timestamp=config.include_timestamp,
            include_request_id=config.include_request_id,
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name. Defaults to 'trix'.

    Returns:
        Logger instance.

    Example:
        >>> logger = get_logger("trix.client")
        >>> logger.info("Client initialized")
    """
    return logging.getLogger(name or "trix")


def generate_request_id() -> str:
    """Generate a unique request ID.

    Returns:
        UUID string for request tracking.
    """
    return str(uuid.uuid4())


def get_request_id() -> Optional[str]:
    """Get the current request ID from context.

    Returns:
        Current request ID or None.
    """
    return _request_id.get()


def set_request_id(request_id: Optional[str] = None) -> str:
    """Set the request ID in context.

    Args:
        request_id: Request ID to set. Generates new ID if None.

    Returns:
        The request ID that was set.
    """
    if request_id is None:
        request_id = generate_request_id()
    _request_id.set(request_id)
    return request_id


def clear_request_id() -> None:
    """Clear the request ID from context."""
    _request_id.set(None)


@contextmanager
def request_context(request_id: Optional[str] = None) -> Iterator[str]:
    """Context manager for request ID tracking.

    Args:
        request_id: Request ID to use. Generates new ID if None.

    Yields:
        The request ID.

    Example:
        >>> with request_context() as req_id:
        ...     logger.info("Processing request")
        ...     # All logs within this block will include req_id
    """
    rid = set_request_id(request_id)
    try:
        yield rid
    finally:
        clear_request_id()


class LoggerAdapter(logging.LoggerAdapter):  # type: ignore[type-arg]
    """Logger adapter that adds extra context to log messages."""

    def __init__(
        self,
        logger: logging.Logger,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(logger, extra or {})

    def process(
        self, msg: str, kwargs: MutableMapping[str, Any]
    ) -> Tuple[str, MutableMapping[str, Any]]:
        """Process log message to add extra context."""
        # Merge extra from adapter with extra from call
        call_extra = kwargs.get("extra", {})
        merged_extra = {**self.extra, **call_extra}
        kwargs["extra"] = merged_extra
        return msg, kwargs

    def with_context(self, **context: Any) -> "LoggerAdapter":
        """Create a new adapter with additional context.

        Args:
            **context: Additional context to add to logs.

        Returns:
            New LoggerAdapter with merged context.

        Example:
            >>> adapter = LoggerAdapter(logger)
            >>> client_logger = adapter.with_context(client_id="client_123")
            >>> client_logger.info("Request started")  # Includes client_id
        """
        merged = {**self.extra, **context}
        return LoggerAdapter(self.logger, merged)


def create_logger_adapter(
    name: Optional[str] = None,
    **context: Any,
) -> LoggerAdapter:
    """Create a logger adapter with initial context.

    Args:
        name: Logger name. Defaults to 'trix'.
        **context: Initial context to add to all logs.

    Returns:
        LoggerAdapter with context.

    Example:
        >>> logger = create_logger_adapter(
        ...     "trix.client",
        ...     sdk_version="1.0.0"
        ... )
        >>> logger.info("Initialized")
    """
    return LoggerAdapter(get_logger(name), context)


# Convenience function for structured logging
def log_request(
    logger: logging.Logger,
    method: str,
    path: str,
    params: Optional[Dict[str, Any]] = None,
    level: int = logging.DEBUG,
) -> None:
    """Log an HTTP request.

    Args:
        logger: Logger instance
        method: HTTP method
        path: Request path
        params: Request parameters
        level: Log level
    """
    from .security import redact_sensitive_data

    safe_params = redact_sensitive_data(params) if params else None
    logger.log(
        level,
        f"Request: {method} {path}",
        extra={"method": method, "path": path, "params": safe_params},
    )


def log_response(
    logger: logging.Logger,
    status_code: int,
    duration_ms: Optional[float] = None,
    level: int = logging.DEBUG,
) -> None:
    """Log an HTTP response.

    Args:
        logger: Logger instance
        status_code: HTTP status code
        duration_ms: Request duration in milliseconds
        level: Log level
    """
    extra: Dict[str, Any] = {"status_code": status_code}
    if duration_ms is not None:
        extra["duration_ms"] = round(duration_ms, 2)

    logger.log(level, f"Response: {status_code}", extra=extra)


def log_error(
    logger: logging.Logger,
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """Log an error with context.

    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Additional context
    """
    from .security import redact_sensitive_data

    extra: Dict[str, Any] = {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }
    if context:
        extra["context"] = redact_sensitive_data(context)

    logger.error(f"Error: {error}", exc_info=error, extra=extra)
