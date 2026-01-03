"""Main Trix client for sync and async operations."""

import logging
from dataclasses import dataclass, field
from types import TracebackType
from typing import (
    Any,
    AsyncIterator,
    BinaryIO,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)

import httpx

from . import MAX_API_VERSION, MIN_API_VERSION, __api_version__, __version__
from .auth import Auth
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
    ValidationError,
)
from .resources import (
    AgentResource,
    ClustersResource,
    EnrichmentsResource,
    EntitiesResource,
    FactsResource,
    FeedbackResource,
    GraphResource,
    HighlightsResource,
    JobsResource,
    MemoriesResource,
    RelationshipsResource,
    SearchResource,
    SpacesResource,
    WebhooksResource,
)
from .resources.agent import AsyncAgentResource
from .resources.clusters import AsyncClustersResource
from .resources.enrichments import AsyncEnrichmentsResource
from .resources.entities import AsyncEntitiesResource
from .resources.facts import AsyncFactsResource
from .resources.feedback import AsyncFeedbackResource
from .resources.graph import AsyncGraphResource
from .resources.highlights import AsyncHighlightsResource
from .resources.jobs import AsyncJobsResource
from .resources.memories import AsyncMemoriesResource
from .resources.relationships import AsyncRelationshipsResource
from .resources.search import AsyncSearchResource
from .resources.spaces import AsyncSpacesResource
from .resources.webhooks import AsyncWebhooksResource
from .utils.retry import RetryConfig
from .utils.security import (
    get_env_credential,
    redact_sensitive_data,
    validate_base_url,
)


@dataclass
class RequestContext:
    """Context passed to request interceptors.

    Attributes:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        path: API endpoint path
        headers: Request headers
        params: Query parameters
        json: JSON body for POST/PUT requests
    """

    method: str
    path: str
    headers: Dict[str, str] = field(default_factory=dict)
    params: Optional[Dict[str, Any]] = None
    json: Optional[Dict[str, Any]] = None


@dataclass
class ResponseContext:
    """Context passed to response interceptors.

    Attributes:
        request: The original request context
        status_code: HTTP response status code
        headers: Response headers
        data: Parsed response data
    """

    request: RequestContext
    status_code: int
    headers: Dict[str, str]
    data: Any


# Interceptor type aliases
RequestInterceptor = Callable[[RequestContext], Optional[RequestContext]]
ResponseInterceptor = Callable[[ResponseContext], Optional[ResponseContext]]
ErrorInterceptor = Callable[[Exception, RequestContext], Exception]

# Async interceptor type aliases
AsyncRequestInterceptor = Callable[[RequestContext], "Optional[RequestContext]"]
AsyncResponseInterceptor = Callable[[ResponseContext], "Optional[ResponseContext]"]
AsyncErrorInterceptor = Callable[[Exception, RequestContext], Exception]


@dataclass
class PoolConfig:
    """
    Connection pool configuration.

    Args:
        max_connections: Maximum number of allowable connections in the pool.
            Default is 100.
        max_keepalive_connections: Maximum number of keep-alive connections.
            Default is 20.
        keepalive_expiry: Time in seconds for keep-alive connections to remain
            idle before being closed. Default is 5 seconds.
    """

    max_connections: int = 100
    max_keepalive_connections: int = 20
    keepalive_expiry: float = 5.0

    def to_httpx_limits(self) -> httpx.Limits:
        """Convert to httpx.Limits object."""
        return httpx.Limits(
            max_connections=self.max_connections,
            max_keepalive_connections=self.max_keepalive_connections,
            keepalive_expiry=self.keepalive_expiry,
        )


logger = logging.getLogger(__name__)


def _safe_log_params(params: Optional[Dict[str, Any]]) -> str:
    """Safely format params for logging, redacting sensitive data."""
    if params is None:
        return "None"
    return str(redact_sensitive_data(params))


def _check_api_version(response: httpx.Response) -> None:
    """
    Check if the API version is compatible with this SDK.

    Args:
        response: HTTP response object

    Raises:
        APIVersionMismatchError: If API version is incompatible
    """
    api_version = response.headers.get("X-API-Version")
    if api_version:
        # Simple version comparison (assumes v1, v2, etc. format)
        try:
            api_num = int(api_version.lstrip("v"))
            min_num = int(MIN_API_VERSION.lstrip("v"))
            max_num = int(MAX_API_VERSION.lstrip("v"))

            if api_num < min_num or api_num > max_num:
                raise APIVersionMismatchError(
                    f"API version {api_version} is not supported by this SDK. "
                    f"Supported versions: {MIN_API_VERSION} to {MAX_API_VERSION}. "
                    f"Please upgrade or downgrade the SDK.",
                    sdk_version=__version__,
                    api_version=api_version,
                    min_supported=MIN_API_VERSION,
                    max_supported=MAX_API_VERSION,
                )
        except ValueError:
            # Non-numeric version format, log warning but continue
            logger.warning(f"Could not parse API version: {api_version}")


def _handle_response(response: httpx.Response) -> None:
    """
    Handle HTTP response and raise appropriate exceptions.

    Args:
        response: HTTP response object

    Raises:
        TrixError: On error responses
    """
    if response.is_success:
        return

    error_data: Optional[Dict[str, Any]] = None
    try:
        error_data = response.json()
        message = error_data.get("message", error_data.get("error", "Unknown error"))
    except Exception:
        message = response.text or f"HTTP {response.status_code}"

    if response.status_code == 401:
        raise AuthenticationError(message, response.status_code, error_data)
    elif response.status_code == 403:
        raise PermissionError(message, response.status_code, error_data)
    elif response.status_code == 404:
        raise NotFoundError(message, response.status_code, error_data)
    elif response.status_code == 422:
        raise ValidationError(message, response.status_code, error_data)
    elif response.status_code == 429:
        retry_after = response.headers.get("Retry-After")
        raise RateLimitError(
            message,
            retry_after=int(retry_after) if retry_after else None,
            status_code=response.status_code,
            response=error_data,
        )
    elif response.status_code >= 500:
        raise ServerError(message, response.status_code, error_data)
    else:
        raise APIError(message, response.status_code, error_data)


class Trix:
    """
    Synchronous Trix client.

    Example:
        >>> # Using environment variable (recommended)
        >>> client = Trix.from_env()
        >>>
        >>> # Or with explicit API key
        >>> client = Trix(api_key="your_api_key")
        >>> memory = client.memories.create(content="Important note")
        >>> print(memory.id)
    """

    @classmethod
    def from_env(
        cls,
        env_var: str = "TRIX_API_KEY",
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_config: Optional[RetryConfig] = None,
        pool_config: Optional[PoolConfig] = None,
    ) -> "Trix":
        """
        Create a Trix client using credentials from environment variables.

        This is the recommended way to create a client for production use.

        Args:
            env_var: Environment variable name for API key (default: TRIX_API_KEY)
            base_url: Base URL (default: from TRIX_BASE_URL or https://api.trixdb.com)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            retry_config: Custom retry configuration
            pool_config: Connection pool configuration

        Returns:
            Configured Trix client

        Raises:
            ValueError: If environment variable is not set

        Example:
            >>> import os
            >>> os.environ["TRIX_API_KEY"] = "your_api_key"
            >>> client = Trix.from_env()
        """
        import os

        api_key = get_env_credential(env_var, required=True)
        base_url = base_url or os.environ.get("TRIX_BASE_URL", "https://api.trixdb.com")

        return cls(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            retry_config=retry_config,
            pool_config=pool_config,
        )

    def __init__(
        self,
        api_key: Optional[str] = None,
        jwt_token: Optional[str] = None,
        base_url: str = "https://api.trixdb.com",
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_config: Optional[RetryConfig] = None,
        pool_config: Optional[PoolConfig] = None,
        allow_insecure: bool = False,
        request_interceptors: Optional[List[RequestInterceptor]] = None,
        response_interceptors: Optional[List[ResponseInterceptor]] = None,
        error_interceptors: Optional[List[ErrorInterceptor]] = None,
    ) -> None:
        """
        Initialize Trix client.

        For production use, prefer Trix.from_env() which reads credentials
        from environment variables.

        Args:
            api_key: API key for authentication
            jwt_token: JWT token for authentication (alternative to api_key)
            base_url: Base URL for Trix API (must be HTTPS)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            retry_config: Custom retry configuration
            pool_config: Connection pool configuration
            allow_insecure: Allow HTTP for local development (NOT for production)
            request_interceptors: List of request interceptors
            response_interceptors: List of response interceptors
            error_interceptors: List of error interceptors

        Raises:
            ValueError: If neither api_key nor jwt_token is provided
            ValueError: If base_url is not a valid HTTPS URL
        """
        self._auth = Auth(api_key=api_key, jwt_token=jwt_token)
        self._base_url = validate_base_url(base_url, allow_http=allow_insecure)
        self._timeout = timeout
        self._retry_config = retry_config or RetryConfig(max_retries=max_retries)
        self._pool_config = pool_config or PoolConfig()

        # Initialize interceptors
        self._request_interceptors: List[RequestInterceptor] = list(request_interceptors or [])
        self._response_interceptors: List[ResponseInterceptor] = list(response_interceptors or [])
        self._error_interceptors: List[ErrorInterceptor] = list(error_interceptors or [])

        # Create HTTP client with connection pooling
        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=timeout,
            headers=self._get_headers(),
            limits=self._pool_config.to_httpx_limits(),
        )

        # Initialize resources
        self.memories = MemoriesResource(self)
        self.relationships = RelationshipsResource(self)
        self.clusters = ClustersResource(self)
        self.spaces = SpacesResource(self)
        self.graph = GraphResource(self)
        self.search = SearchResource(self)
        self.webhooks = WebhooksResource(self)
        self.agent = AgentResource(self)
        self.feedback = FeedbackResource(self)
        self.highlights = HighlightsResource(self)
        self.jobs = JobsResource(self)
        self.facts = FactsResource(self)
        self.entities = EntitiesResource(self)
        self.enrichments = EnrichmentsResource(self)

    def add_request_interceptor(self, interceptor: RequestInterceptor) -> Callable[[], None]:
        """
        Add a request interceptor.

        Args:
            interceptor: Function that receives RequestContext and optionally returns modified context

        Returns:
            Function to remove the interceptor

        Example:
            >>> def log_request(ctx):
            ...     print(f"Request: {ctx.method} {ctx.url}")
            ...     return ctx
            >>> remove = client.add_request_interceptor(log_request)
            >>> # Later: remove()
        """
        self._request_interceptors.append(interceptor)

        def remove() -> None:
            if interceptor in self._request_interceptors:
                self._request_interceptors.remove(interceptor)

        return remove

    def add_response_interceptor(self, interceptor: ResponseInterceptor) -> Callable[[], None]:
        """
        Add a response interceptor.

        Args:
            interceptor: Function that receives ResponseContext and optionally returns modified context

        Returns:
            Function to remove the interceptor
        """
        self._response_interceptors.append(interceptor)

        def remove() -> None:
            if interceptor in self._response_interceptors:
                self._response_interceptors.remove(interceptor)

        return remove

    def add_error_interceptor(self, interceptor: ErrorInterceptor) -> Callable[[], None]:
        """
        Add an error interceptor.

        Args:
            interceptor: Function that receives the error and request context, returns error

        Returns:
            Function to remove the interceptor
        """
        self._error_interceptors.append(interceptor)

        def remove() -> None:
            if interceptor in self._error_interceptors:
                self._error_interceptors.remove(interceptor)

        return remove

    def _run_request_interceptors(self, context: RequestContext) -> RequestContext:
        """Run all request interceptors."""
        ctx = context
        for interceptor in self._request_interceptors:
            result = interceptor(ctx)
            if result is not None:
                ctx = result
        return ctx

    def _run_response_interceptors(self, context: ResponseContext) -> ResponseContext:
        """Run all response interceptors."""
        ctx = context
        for interceptor in self._response_interceptors:
            result = interceptor(ctx)
            if result is not None:
                ctx = result
        return ctx

    def _run_error_interceptors(self, error: Exception, request: RequestContext) -> Exception:
        """Run all error interceptors."""
        err = error
        for interceptor in self._error_interceptors:
            err = interceptor(err, request)
        return err

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication and versioning."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"trix-python-sdk/{__version__}",
            "X-SDK-Version": __version__,
            "X-API-Version": __api_version__,
        }
        headers.update(self._auth.get_headers())
        return headers

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """
        Make HTTP request to Trix API with retry logic.

        Args:
            method: HTTP method
            path: API endpoint path
            params: Query parameters
            json: JSON body
            timeout: Override default timeout for this request (in seconds)

        Returns:
            Response data

        Raises:
            TrixError: On API errors
        """
        import time

        last_exception: Optional[Exception] = None
        config = self._retry_config
        request_timeout = timeout if timeout is not None else self._timeout

        # Create request context for interceptors
        request_context = RequestContext(
            method=method,
            path=path,
            params=params,
            json=json,
            headers=self._get_headers(),
        )

        # Run request interceptors (may modify context)
        request_context = self._run_request_interceptors(request_context)

        for attempt in range(config.max_retries + 1):
            try:
                logger.debug(
                    f"Request: {request_context.method} {request_context.path} params={_safe_log_params(request_context.params)}"
                )
                response = self._client.request(
                    method=request_context.method,
                    url=request_context.path,
                    params=request_context.params,
                    json=request_context.json,
                    timeout=request_timeout,
                )
                # Redact Authorization header from logs
                safe_headers = {
                    k: v if k.lower() != "authorization" else "[REDACTED]"
                    for k, v in response.headers.items()
                }
                logger.debug(f"Response: {response.status_code} headers={safe_headers}")

                # Check API version compatibility
                _check_api_version(response)
                _handle_response(response)

                # Return empty dict for 204 No Content
                if response.status_code == 204:
                    response_data: Any = {}
                else:
                    response_data = response.json()

                # Create response context for interceptors
                response_context = ResponseContext(
                    request=request_context,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    data=response_data,
                )

                # Run response interceptors (may modify context)
                response_context = self._run_response_interceptors(response_context)

                return response_context.data
            except httpx.TimeoutException as e:
                logger.debug(f"Request timed out: {e}")
                exc: Exception = TimeoutError(f"Request timed out: {e}")
                exc = self._run_error_interceptors(exc, request_context)
                raise exc from e
            except httpx.NetworkError as e:
                logger.debug(f"Network error: {e}")
                exc = ConnectionError(f"Network error: {e}")
                exc = self._run_error_interceptors(exc, request_context)
                raise exc from e
            except httpx.HTTPError as e:
                logger.debug(f"HTTP error: {e}")
                exc = APIError(f"HTTP error: {e}")
                exc = self._run_error_interceptors(exc, request_context)
                raise exc from e
            except (RateLimitError, ServerError) as e:
                last_exception = e
                if attempt >= config.max_retries:
                    last_exception = self._run_error_interceptors(e, request_context)
                    raise last_exception

                retry_after = getattr(e, "retry_after", None)
                delay = config.calculate_delay(attempt, retry_after)
                logger.warning(
                    f"Attempt {attempt + 1}/{config.max_retries + 1} failed: {e}. "
                    f"Retrying in {delay:.2f}s..."
                )
                time.sleep(delay)

        if last_exception:
            raise last_exception
        raise RuntimeError("Retry logic failed unexpectedly")

    def _request_raw(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> bytes:
        """
        Make HTTP request and return raw bytes.

        Args:
            method: HTTP method
            path: API endpoint path
            params: Query parameters
            timeout: Override default timeout for this request (in seconds)

        Returns:
            Raw response content

        Raises:
            TrixError: On API errors
        """
        request_timeout = timeout if timeout is not None else self._timeout
        try:
            logger.debug(f"Request (raw): {method} {path} params={params}")
            response = self._client.request(
                method=method, url=path, params=params, timeout=request_timeout
            )
            logger.debug(f"Response (raw): {response.status_code}")
            _check_api_version(response)
            _handle_response(response)
            return response.content
        except httpx.TimeoutException as e:
            logger.debug(f"Request timed out: {e}")
            raise TimeoutError(f"Request timed out: {e}") from e
        except httpx.NetworkError as e:
            logger.debug(f"Network error: {e}")
            raise ConnectionError(f"Network error: {e}") from e
        except httpx.HTTPError as e:
            logger.debug(f"HTTP error: {e}")
            raise APIError(f"HTTP error: {e}") from e

    def _request_stream(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        chunk_size: int = 8192,
        timeout: Optional[float] = None,
    ) -> Iterator[bytes]:
        """
        Make HTTP request and stream the response.

        Args:
            method: HTTP method
            path: API endpoint path
            params: Query parameters
            chunk_size: Size of chunks to yield
            timeout: Override default timeout for this request (in seconds)

        Yields:
            Chunks of response content

        Raises:
            TrixError: On API errors
        """
        request_timeout = timeout if timeout is not None else self._timeout
        try:
            logger.debug(f"Request (stream): {method} {path} params={params}")
            with self._client.stream(
                method=method, url=path, params=params, timeout=request_timeout
            ) as response:
                logger.debug(f"Response (stream): {response.status_code}")
                _check_api_version(response)
                _handle_response(response)
                for chunk in response.iter_bytes(chunk_size=chunk_size):
                    yield chunk
        except httpx.TimeoutException as e:
            logger.debug(f"Request timed out: {e}")
            raise TimeoutError(f"Request timed out: {e}") from e
        except httpx.NetworkError as e:
            logger.debug(f"Network error: {e}")
            raise ConnectionError(f"Network error: {e}") from e
        except httpx.HTTPError as e:
            logger.debug(f"HTTP error: {e}")
            raise APIError(f"HTTP error: {e}") from e

    def _request_multipart(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Union[BinaryIO, Tuple[Any, ...]]]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """
        Make multipart/form-data HTTP request for file uploads.

        Args:
            method: HTTP method
            path: API endpoint path
            data: Form data fields
            files: Files to upload. Can be:
                   - {"file": file_object}
                   - {"file": (filename, file_object)}
                   - {"file": (filename, file_object, content_type)}
            params: Query parameters
            timeout: Override default timeout for this request (in seconds)

        Returns:
            Response data

        Raises:
            TrixError: On API errors
        """
        request_timeout = timeout if timeout is not None else self._timeout
        try:
            logger.debug(f"Request (multipart): {method} {path}")
            # Don't send Content-Type header - let httpx set it with boundary
            headers = {k: v for k, v in self._get_headers().items() if k.lower() != "content-type"}
            response = self._client.request(
                method=method,
                url=path,
                data=data,
                files=files,
                params=params,
                headers=headers,
                timeout=request_timeout,
            )
            logger.debug(f"Response (multipart): {response.status_code}")
            _check_api_version(response)
            _handle_response(response)

            if response.status_code == 204:
                return {}

            return response.json()
        except httpx.TimeoutException as e:
            logger.debug(f"Request timed out: {e}")
            raise TimeoutError(f"Request timed out: {e}") from e
        except httpx.NetworkError as e:
            logger.debug(f"Network error: {e}")
            raise ConnectionError(f"Network error: {e}") from e
        except httpx.HTTPError as e:
            logger.debug(f"HTTP error: {e}")
            raise APIError(f"HTTP error: {e}") from e

    def close(self) -> None:
        """Close the HTTP client and clear credentials."""
        self._client.close()
        # Clear sensitive credentials
        self._auth.clear()
        logger.debug("Client closed and credentials cleared")

    def __enter__(self) -> "Trix":
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Context manager exit."""
        self.close()


class AsyncTrix:
    """
    Asynchronous Trix client.

    Example:
        >>> # Using environment variable (recommended)
        >>> async with AsyncTrix.from_env() as client:
        ...     memory = await client.memories.create(content="Important note")
        ...     print(memory.id)
    """

    @classmethod
    def from_env(
        cls,
        env_var: str = "TRIX_API_KEY",
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_config: Optional[RetryConfig] = None,
        pool_config: Optional[PoolConfig] = None,
    ) -> "AsyncTrix":
        """
        Create an async Trix client using credentials from environment variables.

        This is the recommended way to create a client for production use.

        Args:
            env_var: Environment variable name for API key (default: TRIX_API_KEY)
            base_url: Base URL (default: from TRIX_BASE_URL or https://api.trixdb.com)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            retry_config: Custom retry configuration
            pool_config: Connection pool configuration

        Returns:
            Configured AsyncTrix client

        Raises:
            ValueError: If environment variable is not set
        """
        import os

        api_key = get_env_credential(env_var, required=True)
        base_url = base_url or os.environ.get("TRIX_BASE_URL", "https://api.trixdb.com")

        return cls(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            retry_config=retry_config,
            pool_config=pool_config,
        )

    def __init__(
        self,
        api_key: Optional[str] = None,
        jwt_token: Optional[str] = None,
        base_url: str = "https://api.trixdb.com",
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_config: Optional[RetryConfig] = None,
        pool_config: Optional[PoolConfig] = None,
        allow_insecure: bool = False,
        request_interceptors: Optional[List[RequestInterceptor]] = None,
        response_interceptors: Optional[List[ResponseInterceptor]] = None,
        error_interceptors: Optional[List[ErrorInterceptor]] = None,
    ) -> None:
        """
        Initialize async Trix client.

        For production use, prefer AsyncTrix.from_env() which reads credentials
        from environment variables.

        Args:
            api_key: API key for authentication
            jwt_token: JWT token for authentication (alternative to api_key)
            base_url: Base URL for Trix API (must be HTTPS)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            retry_config: Custom retry configuration
            pool_config: Connection pool configuration
            allow_insecure: Allow HTTP for local development (NOT for production)
            request_interceptors: List of request interceptors
            response_interceptors: List of response interceptors
            error_interceptors: List of error interceptors

        Raises:
            ValueError: If neither api_key nor jwt_token is provided
            ValueError: If base_url is not a valid HTTPS URL
        """
        self._auth = Auth(api_key=api_key, jwt_token=jwt_token)
        self._base_url = validate_base_url(base_url, allow_http=allow_insecure)
        self._timeout = timeout
        self._retry_config = retry_config or RetryConfig(max_retries=max_retries)
        self._pool_config = pool_config or PoolConfig()

        # Initialize interceptors
        self._request_interceptors: List[RequestInterceptor] = list(request_interceptors or [])
        self._response_interceptors: List[ResponseInterceptor] = list(response_interceptors or [])
        self._error_interceptors: List[ErrorInterceptor] = list(error_interceptors or [])

        # Create async HTTP client with connection pooling
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=timeout,
            headers=self._get_headers(),
            limits=self._pool_config.to_httpx_limits(),
        )

        # Initialize async resources
        self.memories = AsyncMemoriesResource(self)
        self.relationships = AsyncRelationshipsResource(self)
        self.clusters = AsyncClustersResource(self)
        self.spaces = AsyncSpacesResource(self)
        self.graph = AsyncGraphResource(self)
        self.search = AsyncSearchResource(self)
        self.webhooks = AsyncWebhooksResource(self)
        self.agent = AsyncAgentResource(self)
        self.feedback = AsyncFeedbackResource(self)
        self.highlights = AsyncHighlightsResource(self)
        self.jobs = AsyncJobsResource(self)
        self.facts = AsyncFactsResource(self)
        self.entities = AsyncEntitiesResource(self)
        self.enrichments = AsyncEnrichmentsResource(self)

    def add_request_interceptor(self, interceptor: RequestInterceptor) -> Callable[[], None]:
        """
        Add a request interceptor.

        Args:
            interceptor: Function that receives RequestContext and optionally returns modified context

        Returns:
            Function to remove the interceptor
        """
        self._request_interceptors.append(interceptor)

        def remove() -> None:
            if interceptor in self._request_interceptors:
                self._request_interceptors.remove(interceptor)

        return remove

    def add_response_interceptor(self, interceptor: ResponseInterceptor) -> Callable[[], None]:
        """
        Add a response interceptor.

        Args:
            interceptor: Function that receives ResponseContext and optionally returns modified context

        Returns:
            Function to remove the interceptor
        """
        self._response_interceptors.append(interceptor)

        def remove() -> None:
            if interceptor in self._response_interceptors:
                self._response_interceptors.remove(interceptor)

        return remove

    def add_error_interceptor(self, interceptor: ErrorInterceptor) -> Callable[[], None]:
        """
        Add an error interceptor.

        Args:
            interceptor: Function that receives the error and request context, returns error

        Returns:
            Function to remove the interceptor
        """
        self._error_interceptors.append(interceptor)

        def remove() -> None:
            if interceptor in self._error_interceptors:
                self._error_interceptors.remove(interceptor)

        return remove

    def _run_request_interceptors(self, context: RequestContext) -> RequestContext:
        """Run all request interceptors."""
        ctx = context
        for interceptor in self._request_interceptors:
            result = interceptor(ctx)
            if result is not None:
                ctx = result
        return ctx

    def _run_response_interceptors(self, context: ResponseContext) -> ResponseContext:
        """Run all response interceptors."""
        ctx = context
        for interceptor in self._response_interceptors:
            result = interceptor(ctx)
            if result is not None:
                ctx = result
        return ctx

    def _run_error_interceptors(self, error: Exception, request: RequestContext) -> Exception:
        """Run all error interceptors."""
        err = error
        for interceptor in self._error_interceptors:
            err = interceptor(err, request)
        return err

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication and versioning."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"trix-python-sdk/{__version__}",
            "X-SDK-Version": __version__,
            "X-API-Version": __api_version__,
        }
        headers.update(self._auth.get_headers())
        return headers

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """
        Make async HTTP request to Trix API with retry logic.

        Args:
            method: HTTP method
            path: API endpoint path
            params: Query parameters
            json: JSON body
            timeout: Override default timeout for this request (in seconds)

        Returns:
            Response data

        Raises:
            TrixError: On API errors
        """
        import asyncio

        last_exception: Optional[Exception] = None
        config = self._retry_config
        request_timeout = timeout if timeout is not None else self._timeout

        # Create request context for interceptors
        request_context = RequestContext(
            method=method,
            path=path,
            params=params,
            json=json,
            headers=self._get_headers(),
        )

        # Run request interceptors (may modify context)
        request_context = self._run_request_interceptors(request_context)

        for attempt in range(config.max_retries + 1):
            try:
                logger.debug(
                    f"Request: {request_context.method} {request_context.path} params={_safe_log_params(request_context.params)}"
                )
                response = await self._client.request(
                    method=request_context.method,
                    url=request_context.path,
                    params=request_context.params,
                    json=request_context.json,
                    timeout=request_timeout,
                )
                # Redact Authorization header from logs
                safe_headers = {
                    k: v if k.lower() != "authorization" else "[REDACTED]"
                    for k, v in response.headers.items()
                }
                logger.debug(f"Response: {response.status_code} headers={safe_headers}")

                # Check API version compatibility
                _check_api_version(response)
                _handle_response(response)

                # Return empty dict for 204 No Content
                if response.status_code == 204:
                    response_data: Any = {}
                else:
                    response_data = response.json()

                # Create response context for interceptors
                response_context = ResponseContext(
                    request=request_context,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    data=response_data,
                )

                # Run response interceptors (may modify context)
                response_context = self._run_response_interceptors(response_context)

                return response_context.data
            except httpx.TimeoutException as e:
                logger.debug(f"Request timed out: {e}")
                exc: Exception = TimeoutError(f"Request timed out: {e}")
                exc = self._run_error_interceptors(exc, request_context)
                raise exc from e
            except httpx.NetworkError as e:
                logger.debug(f"Network error: {e}")
                exc = ConnectionError(f"Network error: {e}")
                exc = self._run_error_interceptors(exc, request_context)
                raise exc from e
            except httpx.HTTPError as e:
                logger.debug(f"HTTP error: {e}")
                exc = APIError(f"HTTP error: {e}")
                exc = self._run_error_interceptors(exc, request_context)
                raise exc from e
            except (RateLimitError, ServerError) as e:
                last_exception = e
                if attempt >= config.max_retries:
                    last_exception = self._run_error_interceptors(e, request_context)
                    raise last_exception

                retry_after = getattr(e, "retry_after", None)
                delay = config.calculate_delay(attempt, retry_after)
                logger.warning(
                    f"Attempt {attempt + 1}/{config.max_retries + 1} failed: {e}. "
                    f"Retrying in {delay:.2f}s..."
                )
                await asyncio.sleep(delay)

        if last_exception:
            raise last_exception
        raise RuntimeError("Retry logic failed unexpectedly")

    async def _request_raw(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> bytes:
        """
        Make async HTTP request and return raw bytes.

        Args:
            method: HTTP method
            path: API endpoint path
            params: Query parameters
            timeout: Override default timeout for this request (in seconds)

        Returns:
            Raw response content

        Raises:
            TrixError: On API errors
        """
        request_timeout = timeout if timeout is not None else self._timeout
        try:
            logger.debug(f"Request (raw): {method} {path} params={params}")
            response = await self._client.request(
                method=method, url=path, params=params, timeout=request_timeout
            )
            logger.debug(f"Response (raw): {response.status_code}")
            _check_api_version(response)
            _handle_response(response)
            return response.content
        except httpx.TimeoutException as e:
            logger.debug(f"Request timed out: {e}")
            raise TimeoutError(f"Request timed out: {e}") from e
        except httpx.NetworkError as e:
            logger.debug(f"Network error: {e}")
            raise ConnectionError(f"Network error: {e}") from e
        except httpx.HTTPError as e:
            logger.debug(f"HTTP error: {e}")
            raise APIError(f"HTTP error: {e}") from e

    async def _request_stream(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        chunk_size: int = 8192,
        timeout: Optional[float] = None,
    ) -> AsyncIterator[bytes]:
        """
        Make async HTTP request and stream the response.

        Args:
            method: HTTP method
            path: API endpoint path
            params: Query parameters
            chunk_size: Size of chunks to yield
            timeout: Override default timeout for this request (in seconds)

        Yields:
            Chunks of response content

        Raises:
            TrixError: On API errors
        """
        request_timeout = timeout if timeout is not None else self._timeout
        try:
            logger.debug(f"Request (stream): {method} {path} params={params}")
            async with self._client.stream(
                method=method, url=path, params=params, timeout=request_timeout
            ) as response:
                logger.debug(f"Response (stream): {response.status_code}")
                _check_api_version(response)
                _handle_response(response)
                async for chunk in response.aiter_bytes(chunk_size=chunk_size):
                    yield chunk
        except httpx.TimeoutException as e:
            logger.debug(f"Request timed out: {e}")
            raise TimeoutError(f"Request timed out: {e}") from e
        except httpx.NetworkError as e:
            logger.debug(f"Network error: {e}")
            raise ConnectionError(f"Network error: {e}") from e
        except httpx.HTTPError as e:
            logger.debug(f"HTTP error: {e}")
            raise APIError(f"HTTP error: {e}") from e

    async def _request_multipart(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Union[BinaryIO, Tuple[Any, ...]]]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """
        Make async multipart/form-data HTTP request for file uploads.

        Args:
            method: HTTP method
            path: API endpoint path
            data: Form data fields
            files: Files to upload. Can be:
                   - {"file": file_object}
                   - {"file": (filename, file_object)}
                   - {"file": (filename, file_object, content_type)}
            params: Query parameters
            timeout: Override default timeout for this request (in seconds)

        Returns:
            Response data

        Raises:
            TrixError: On API errors
        """
        request_timeout = timeout if timeout is not None else self._timeout
        try:
            logger.debug(f"Request (multipart): {method} {path}")
            # Don't send Content-Type header - let httpx set it with boundary
            headers = {k: v for k, v in self._get_headers().items() if k.lower() != "content-type"}
            response = await self._client.request(
                method=method,
                url=path,
                data=data,
                files=files,
                params=params,
                headers=headers,
                timeout=request_timeout,
            )
            logger.debug(f"Response (multipart): {response.status_code}")
            _check_api_version(response)
            _handle_response(response)

            if response.status_code == 204:
                return {}

            return response.json()
        except httpx.TimeoutException as e:
            logger.debug(f"Request timed out: {e}")
            raise TimeoutError(f"Request timed out: {e}") from e
        except httpx.NetworkError as e:
            logger.debug(f"Network error: {e}")
            raise ConnectionError(f"Network error: {e}") from e
        except httpx.HTTPError as e:
            logger.debug(f"HTTP error: {e}")
            raise APIError(f"HTTP error: {e}") from e

    async def close(self) -> None:
        """Close the async HTTP client and clear credentials."""
        await self._client.aclose()
        # Clear sensitive credentials
        self._auth.clear()
        logger.debug("Async client closed and credentials cleared")

    async def __aenter__(self) -> "AsyncTrix":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Async context manager exit."""
        await self.close()
