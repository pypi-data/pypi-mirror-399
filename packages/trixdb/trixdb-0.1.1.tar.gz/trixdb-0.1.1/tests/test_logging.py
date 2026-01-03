"""Tests for Trix structured logging utilities."""

import json
import logging
from io import StringIO


from trix.utils.logging import (
    LogConfig,
    LogFormat,
    LogLevel,
    LoggerAdapter,
    clear_request_id,
    create_logger_adapter,
    generate_request_id,
    get_logger,
    get_request_id,
    log_error,
    log_request,
    log_response,
    request_context,
    set_request_id,
    setup_logging,
)


class TestLogConfig:
    """Tests for LogConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = LogConfig()
        assert config.level == LogLevel.INFO
        assert config.format == LogFormat.TEXT
        assert config.include_timestamp is True
        assert config.include_request_id is True
        assert config.redact_sensitive is True
        assert config.logger_name == "trix"

    def test_custom_values(self):
        """Test custom configuration values."""
        config = LogConfig(
            level=LogLevel.DEBUG,
            format=LogFormat.JSON,
            include_timestamp=False,
            include_request_id=False,
            redact_sensitive=False,
            logger_name="custom",
        )
        assert config.level == LogLevel.DEBUG
        assert config.format == LogFormat.JSON
        assert config.include_timestamp is False
        assert config.include_request_id is False
        assert config.redact_sensitive is False
        assert config.logger_name == "custom"


class TestLogLevel:
    """Tests for LogLevel enum."""

    def test_log_levels(self):
        """Test log level values."""
        assert LogLevel.DEBUG.value == "DEBUG"
        assert LogLevel.INFO.value == "INFO"
        assert LogLevel.WARNING.value == "WARNING"
        assert LogLevel.ERROR.value == "ERROR"
        assert LogLevel.CRITICAL.value == "CRITICAL"


class TestLogFormat:
    """Tests for LogFormat enum."""

    def test_log_formats(self):
        """Test log format values."""
        assert LogFormat.TEXT.value == "text"
        assert LogFormat.JSON.value == "json"


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_returns_logger(self):
        """Test setup_logging returns a logger."""
        logger = setup_logging()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "trix"

    def test_sets_level(self):
        """Test setup_logging sets the log level."""
        config = LogConfig(level=LogLevel.DEBUG)
        logger = setup_logging(config)
        assert logger.level == logging.DEBUG

    def test_custom_logger_name(self):
        """Test setup_logging with custom logger name."""
        config = LogConfig(logger_name="custom_logger")
        logger = setup_logging(config)
        assert logger.name == "custom_logger"


class TestGetLogger:
    """Tests for get_logger function."""

    def test_get_default_logger(self):
        """Test getting default logger."""
        logger = get_logger()
        assert logger.name == "trix"

    def test_get_named_logger(self):
        """Test getting named logger."""
        logger = get_logger("trix.client")
        assert logger.name == "trix.client"


class TestRequestId:
    """Tests for request ID functions."""

    def test_generate_request_id(self):
        """Test generating request ID."""
        req_id = generate_request_id()
        assert isinstance(req_id, str)
        assert len(req_id) == 36  # UUID format

    def test_set_and_get_request_id(self):
        """Test setting and getting request ID."""
        clear_request_id()  # Clear any existing
        assert get_request_id() is None

        req_id = set_request_id("test-123")
        assert req_id == "test-123"
        assert get_request_id() == "test-123"

        clear_request_id()
        assert get_request_id() is None

    def test_set_request_id_generates_if_none(self):
        """Test set_request_id generates ID if none provided."""
        clear_request_id()
        req_id = set_request_id()
        assert req_id is not None
        assert len(req_id) == 36
        clear_request_id()


class TestRequestContext:
    """Tests for request_context context manager."""

    def test_request_context_sets_and_clears(self):
        """Test request_context sets and clears request ID."""
        clear_request_id()
        assert get_request_id() is None

        with request_context() as req_id:
            assert get_request_id() == req_id
            assert len(req_id) == 36

        assert get_request_id() is None

    def test_request_context_with_custom_id(self):
        """Test request_context with custom ID."""
        clear_request_id()

        with request_context("custom-id") as req_id:
            assert req_id == "custom-id"
            assert get_request_id() == "custom-id"

        assert get_request_id() is None


class TestLoggerAdapter:
    """Tests for LoggerAdapter."""

    def test_create_adapter(self):
        """Test creating logger adapter."""
        logger = get_logger("test")
        adapter = LoggerAdapter(logger)
        assert adapter.logger == logger
        assert adapter.extra == {}

    def test_adapter_with_context(self):
        """Test adapter with context."""
        logger = get_logger("test")
        adapter = LoggerAdapter(logger, {"key": "value"})
        assert adapter.extra == {"key": "value"}

    def test_with_context_creates_new_adapter(self):
        """Test with_context creates new adapter."""
        logger = get_logger("test")
        adapter1 = LoggerAdapter(logger, {"key1": "value1"})
        adapter2 = adapter1.with_context(key2="value2")

        assert adapter2 is not adapter1
        assert adapter2.extra == {"key1": "value1", "key2": "value2"}
        assert adapter1.extra == {"key1": "value1"}


class TestCreateLoggerAdapter:
    """Tests for create_logger_adapter function."""

    def test_create_with_default_name(self):
        """Test creating adapter with default name."""
        adapter = create_logger_adapter()
        assert adapter.logger.name == "trix"

    def test_create_with_custom_name(self):
        """Test creating adapter with custom name."""
        adapter = create_logger_adapter("custom")
        assert adapter.logger.name == "custom"

    def test_create_with_context(self):
        """Test creating adapter with initial context."""
        adapter = create_logger_adapter(version="1.0.0")
        assert adapter.extra["version"] == "1.0.0"


class TestJsonFormatter:
    """Tests for JSON log formatting."""

    def test_json_format_output(self):
        """Test JSON format produces valid JSON."""
        stream = StringIO()
        config = LogConfig(
            level=LogLevel.DEBUG,
            format=LogFormat.JSON,
            stream=stream,
        )
        logger = setup_logging(config)
        logger.info("Test message")

        output = stream.getvalue()
        # Parse as JSON to verify it's valid
        log_entry = json.loads(output.strip())
        assert log_entry["level"] == "INFO"
        assert log_entry["message"] == "Test message"
        assert "timestamp" in log_entry


class TestTextFormatter:
    """Tests for text log formatting."""

    def test_text_format_output(self):
        """Test text format produces expected output."""
        stream = StringIO()
        config = LogConfig(
            level=LogLevel.DEBUG,
            format=LogFormat.TEXT,
            stream=stream,
        )
        logger = setup_logging(config)
        logger.info("Test message")

        output = stream.getvalue()
        assert "INFO" in output
        assert "Test message" in output
        assert "trix" in output


class TestLogHelpers:
    """Tests for log helper functions."""

    def test_log_request(self):
        """Test log_request function."""
        stream = StringIO()
        config = LogConfig(level=LogLevel.DEBUG, stream=stream)
        logger = setup_logging(config)

        log_request(logger, "GET", "/memories", {"limit": 10})

        output = stream.getvalue()
        assert "GET" in output
        assert "/memories" in output

    def test_log_response(self):
        """Test log_response function."""
        stream = StringIO()
        config = LogConfig(level=LogLevel.DEBUG, stream=stream)
        logger = setup_logging(config)

        log_response(logger, 200, duration_ms=50.5)

        output = stream.getvalue()
        assert "200" in output

    def test_log_error(self):
        """Test log_error function."""
        stream = StringIO()
        config = LogConfig(level=LogLevel.DEBUG, stream=stream)
        logger = setup_logging(config)

        error = ValueError("Test error")
        log_error(logger, error, {"request_path": "/memories"})

        output = stream.getvalue()
        assert "ValueError" in output or "Test error" in output


class TestSensitiveDataRedaction:
    """Tests for sensitive data redaction in logs."""

    def test_redacts_api_key_in_json_format(self):
        """Test API key is redacted in JSON logs."""
        stream = StringIO()
        config = LogConfig(
            level=LogLevel.DEBUG,
            format=LogFormat.JSON,
            redact_sensitive=True,
            stream=stream,
        )
        logger = setup_logging(config)

        # Create a custom log record with extra data
        class ExtraLogger(logging.LoggerAdapter):
            def process(self, msg, kwargs):
                kwargs["extra"] = {"extra": {"api_key": "secret123"}}
                return msg, kwargs

        extra_logger = ExtraLogger(logger, {})
        extra_logger.info("Test with sensitive data")

        output = stream.getvalue()
        # The actual API key should not appear in the output
        assert "secret123" not in output
