"""
GLPI Python SDK - Connection Module

Manages connections to the GLPI API.
Supports synchronous and asynchronous modes.
"""

from __future__ import annotations

from base64 import b64encode
from functools import wraps
from typing import Literal, TypeAlias

from .exceptions import (
    # Aliases for compatibility
    ForbiddenError,
    InvalidCredentialsError,
    # Resource errors
    ItemDoesNotExistError,
    SessionTokenError,
    UnauthorizedError,
)
from .helpers import get_item_url, parse_kwargs
from .http_client import AsyncHTTPClient, ClientConfig, HTTPClient

# Type aliases
GlpiType: TypeAlias = str
ResourceId: TypeAlias = int
Url: TypeAlias = str


class URLs:
    """Specific GLPI API URL Suffixes."""

    LOGIN: Url = "initSession"
    LOGOUT: Url = "killSession"
    RESOURCE_SEARCH: Url = "search"
    SEARCH_OPTIONS: Url = "listSearchOptions"
    GET_MULTIPLE_ITEMS: Url = "getMultipleItems"
    DOCUMENTS: Url = "Document"


class GLPISession:
    """
    A class that wraps a GLPI connection with all its API endpoints.

    Instantiating this class will create an authenticated GLPI HTTP session
    using the specified authentication type.

    Usage example:
        ```python
        # Basic authentication
        session = GLPISession(
            api_url="https://glpi.example.com/apirest.php",
            app_token="your_app_token",
            auth_type="basic",
            user="admin",
            password="password",
            timeout=30.0
        )

        # Using context manager (recommended)
        with GLPISession(...) as session:
            tickets = session.get_all_items("Ticket")
        ```
    """

    def __init__(
        self,
        api_url: Url = None,
        app_token: str = None,
        auth_type: Literal["basic", "user_token"] = "basic",
        user: str = None,
        password: str = None,
        user_token: str = None,
        # New configuration parameters
        timeout: float = 30.0,
        connect_timeout: float = 10.0,
        verify_ssl: bool = True,
        max_retries: int = 3,
        auto_refresh_token: bool = True,
        **session_request_kwargs,
    ):
        """
        Initialize the GLPI session.

        Args:
            api_url: GLPI API base URL (e.g., https://glpi.example.com/apirest.php)
            app_token: GLPI application token
            auth_type: Authentication type ("basic" or "user_token")
            user: Username (for auth_type="basic")
            password: Password (for auth_type="basic")
            user_token: User token (for auth_type="user_token")
            timeout: Default request timeout (seconds)
            connect_timeout: Connection timeout (seconds)
            verify_ssl: Verify SSL certificates
            max_retries: Maximum number of retries on failure
            auto_refresh_token: Automatically refresh token on 401/403
        """
        # Validations
        if not api_url:
            raise ValueError("API URL is required for GLPI Session.")
        if not app_token:
            raise ValueError("App token is required for GLPI Session.")
        if auth_type not in ["basic", "user_token"]:
            raise ValueError(f"Invalid auth type: {auth_type}. Use 'basic' or 'user_token'.")

        if auth_type == "basic":
            if not user or not password:
                raise ValueError("User and password are required for basic authentication.")
        elif auth_type == "user_token":
            if not user_token:
                raise ValueError("User token is required for user_token authentication.")

        self.api_url: Url = api_url
        self.auth_type = auth_type
        self.user = user
        self._password = password
        self._app_token = app_token
        self.user_token = user_token
        self.auto_refresh_token = auto_refresh_token
        self._session_token: str | None = None

        # HTTP client configuration
        self._client_config = ClientConfig(
            timeout=timeout,
            connect_timeout=connect_timeout,
            verify_ssl=verify_ssl,
            max_retries=max_retries,
        )

        # Keep extra kwargs for compatibility
        self._extra_kwargs = session_request_kwargs

        # Initialize HTTP client (httpx)
        self._http_client = HTTPClient(config=self._client_config)

        # Get session token and configure headers
        self._initialize_session()

    def _initialize_session(self) -> None:
        """Initialize the session by obtaining the token."""
        self._session_token = self._get_session_token()
        self._http_client.set_headers(self._get_request_headers())

    def _get_authorization(self) -> str:
        """Generate authorization string based on auth type."""
        if self.auth_type == "user_token":
            return f"user_token {self.user_token}"
        elif self.auth_type == "basic":
            credentials = f"{self.user}:{self._password}"
            b64_bytes = b64encode(credentials.encode("utf8"))
            return f"Basic {b64_bytes.decode('ascii')}"

    def _get_session_token(self) -> str:
        """Obtain a new session token from GLPI."""
        url = get_item_url(self.api_url, URLs.LOGIN)
        authorization_string = self._get_authorization()

        response = self._http_client.get(
            url,
            headers={
                "Content-Type": "application/json",
                "App-Token": self._app_token,
                "Authorization": authorization_string,
            },
        )

        if response.status_code == 401:
            raise InvalidCredentialsError(
                "Provided credentials are invalid",
                details=response.json() if response.text else None,
            )

        if response.status_code == 400:
            raise SessionTokenError(
                "Failed to obtain session token", details=response.json() if response.text else None
            )

        data = response.json()
        token = data.get("session_token")

        if not token:
            raise SessionTokenError("Session token not found in response", details=data)

        return token

    def _get_request_headers(self) -> dict[str, str]:
        """Return default headers for authenticated requests."""
        return {
            "Accept": "application/json",
            "App-Token": self._app_token,
            "Session-Token": self._session_token,
        }

    def refresh_session(self) -> None:
        """Force session token renewal."""
        self._session_token = self._get_session_token()
        self._http_client.set_headers(self._get_request_headers())

    def close(self) -> None:
        """Close the GLPI session and HTTP client."""
        try:
            # Try to logout from GLPI
            url = get_item_url(self.api_url, URLs.LOGOUT)
            self._http_client.get(url)
        except Exception:
            pass  # Ignore logout errors
        finally:
            self._http_client.close()

    def __enter__(self) -> GLPISession:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    # =========================================================================
    # Property for legacy session access compatibility
    # =========================================================================

    @property
    def session(self) -> HTTPClient:
        """Access to HTTP client (legacy code compatibility)."""
        return self._http_client

    # =========================================================================
    # Decorator for request handling
    # =========================================================================

    @staticmethod
    def _request_handler(func):
        """Decorator for response parsing and retry on 401/403."""

        @wraps(func)
        def wrapper(self: GLPISession, *args, **kwargs):
            try:
                response = func(self, *args, **kwargs)

                # Verifica erro específico do GLPI
                if response.status_code == 400:
                    try:
                        data = response.json()
                        if (
                            isinstance(data, list)
                            and data[0] == "ERROR_RESOURCE_NOT_FOUND_NOR_COMMONDBTM"
                        ):
                            raise ItemDoesNotExistError(
                                message=f"Requested item on {func.__name__} does not exist",
                                details={"args": args, "kwargs": kwargs, "url": str(response.url)},
                            )
                    except (ValueError, KeyError, IndexError):
                        pass

                return response

            except (UnauthorizedError, ForbiddenError):
                # Automatic retry with new token
                if self.auto_refresh_token:
                    self.refresh_session()
                    return func(self, *args, **kwargs)
                raise

        return wrapper

    # Keep old decorator as alias for compatibility
    request = _request_handler

    # =========================================================================
    # API Methods
    # =========================================================================

    @_request_handler
    def get_item(self, item_type: GlpiType, id: ResourceId, **kwargs):
        """Get a specific item by ID."""
        url = get_item_url(self.api_url, item_type) + f"/{id}"
        kwargs = parse_kwargs(kwargs)
        return self._http_client.get(url, params=kwargs)

    @_request_handler
    def get_multiple_items(self, *item_keys: dict, **kwargs):
        """Get multiple items using key composition {"itemtype":..., "items_id":...}."""
        url = get_item_url(self.api_url, URLs.GET_MULTIPLE_ITEMS) + "?"
        url += "&".join(
            [
                f"items[{i}][itemtype]={item['itemtype']}&items[{i}][items_id]={item['items_id']}"
                for i, item in enumerate(item_keys)
            ]
        )
        kwargs = parse_kwargs(kwargs)
        return self._http_client.get(url, params=kwargs)

    @_request_handler
    def get_all_items(self, item_type: GlpiType, **kwargs):
        """Get all items of a type."""
        url = get_item_url(self.api_url, item_type)
        kwargs = parse_kwargs(kwargs)
        return self._http_client.get(url, params=kwargs)

    @_request_handler
    def create_item(self, item_type: GlpiType, **kwargs):
        """Create a new item."""
        url = get_item_url(self.api_url, item_type)
        body = {"input": kwargs}
        return self._http_client.post(url, json=body)

    @_request_handler
    def update_item(self, item_type: GlpiType, id: ResourceId, **kwargs):
        """Update an existing item."""
        url = get_item_url(self.api_url, item_type) + f"/{id}"
        body = {"input": kwargs}
        return self._http_client.put(url, json=body)

    @_request_handler
    def delete_item(self, item_type: GlpiType, id: ResourceId):
        """Delete an item."""
        url = get_item_url(self.api_url, item_type) + f"/{id}"
        return self._http_client.delete(url)

    @_request_handler
    def create_items(self, item_type: GlpiType, *args: dict):
        """Create multiple items."""
        url = get_item_url(self.api_url, item_type)
        body = {"input": list(args)}
        return self._http_client.post(url, json=body)

    @_request_handler
    def get_item_search_options(self, item_type: GlpiType):
        """Get search options for an item type."""
        url = get_item_url(self.api_url, URLs.SEARCH_OPTIONS) + f"/{item_type}"
        return self._http_client.get(url)

    @_request_handler
    def search_items(self, item_type: GlpiType, criteria, **kwargs):
        """Search items using criteria."""
        search_opts: dict = self.get_item_search_options(item_type).json()
        criterias: list[dict] = [ev.as_dict() for ev in criteria._evaluation]

        # Find the field ID by name
        for eval_item in criterias:
            field_ids = [
                k
                for k, v in search_opts.items()
                if isinstance(v, dict) and v.get("uid", "").lower() == eval_item["field"]
            ]
            if not field_ids:
                valid_opts = {
                    v.get("uid"): v.get("name")
                    for k, v in search_opts.items()
                    if k != "common" and isinstance(v, dict)
                }
                raise ValueError(
                    f"Couldn't find a valid filtering field with uid '{eval_item['field']}' "
                    f"for itemtype '{item_type}'. Valid options:\n\n{valid_opts}"
                )
            eval_item["field"] = field_ids[0]

        url = get_item_url(self.api_url, URLs.RESOURCE_SEARCH) + item_type + "/?"
        criteria_kwargs = [
            [f"criteria[{i}][{k}]={v}" for k, v in crit.items()] for i, crit in enumerate(criterias)
        ]

        if criteria_kwargs:
            kwargs = parse_kwargs(kwargs)
            url += "&".join(criteria_kwargs[0] + [f"{k}={v}" for k, v in kwargs.items()])

        url += "&forcedisplay[0]=2"

        return self._http_client.get(url)

    @_request_handler
    def download_document(self, document_id: int, **kwargs):
        """Download a document."""
        url = get_item_url(self.api_url, URLs.DOCUMENTS) + f"/{document_id}?alt=media"
        return self._http_client.get(url, params=kwargs)


# =============================================================================
# Async Version
# =============================================================================


class AsyncGLPISession:
    """
    Async version of the GLPI session.

    Compatible with FastAPI and other async frameworks.

    Usage example:
        ```python
        async with AsyncGLPISession(
            api_url="https://glpi.example.com/apirest.php",
            app_token="your_app_token",
            auth_type="basic",
            user="admin",
            password="password"
        ) as session:
            tickets = await session.get_all_items("Ticket")
        ```
    """

    def __init__(
        self,
        api_url: Url = None,
        app_token: str = None,
        auth_type: Literal["basic", "user_token"] = "basic",
        user: str = None,
        password: str = None,
        user_token: str = None,
        timeout: float = 30.0,
        connect_timeout: float = 10.0,
        verify_ssl: bool = True,
        max_retries: int = 3,
        auto_refresh_token: bool = True,
        **session_request_kwargs,
    ):
        # Validações
        if not api_url:
            raise ValueError("API URL is required for GLPI Session.")
        if not app_token:
            raise ValueError("App token is required for GLPI Session.")
        if auth_type not in ["basic", "user_token"]:
            raise ValueError(f"Invalid auth type: {auth_type}")

        if auth_type == "basic" and (not user or not password):
            raise ValueError("User and password are required for basic authentication.")
        elif auth_type == "user_token" and not user_token:
            raise ValueError("User token is required for user_token authentication.")

        self.api_url: Url = api_url
        self.auth_type = auth_type
        self.user = user
        self._password = password
        self._app_token = app_token
        self.user_token = user_token
        self.auto_refresh_token = auto_refresh_token
        self._session_token: str | None = None
        self._initialized = False

        self._client_config = ClientConfig(
            timeout=timeout,
            connect_timeout=connect_timeout,
            verify_ssl=verify_ssl,
            max_retries=max_retries,
        )

        self._http_client = AsyncHTTPClient(config=self._client_config)

    async def _initialize_session(self) -> None:
        """Inicializa a sessão assíncrona."""
        if not self._initialized:
            self._session_token = await self._get_session_token()
            self._http_client.set_headers(self._get_request_headers())
            self._initialized = True

    def _get_authorization(self) -> str:
        if self.auth_type == "user_token":
            return f"user_token {self.user_token}"
        elif self.auth_type == "basic":
            credentials = f"{self.user}:{self._password}"
            b64_bytes = b64encode(credentials.encode("utf8"))
            return f"Basic {b64_bytes.decode('ascii')}"

    async def _get_session_token(self) -> str:
        url = get_item_url(self.api_url, URLs.LOGIN)
        authorization_string = self._get_authorization()

        response = await self._http_client.get(
            url,
            headers={
                "Content-Type": "application/json",
                "App-Token": self._app_token,
                "Authorization": authorization_string,
            },
        )

        if response.status_code == 401:
            raise InvalidCredentialsError(
                "Provided credentials are invalid",
                details=response.json() if response.text else None,
            )

        if response.status_code == 400:
            raise SessionTokenError(
                "Failed to obtain session token", details=response.json() if response.text else None
            )

        data = response.json()
        token = data.get("session_token")

        if not token:
            raise SessionTokenError("Session token not found in response", details=data)

        return token

    def _get_request_headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json",
            "App-Token": self._app_token,
            "Session-Token": self._session_token,
        }

    async def refresh_session(self) -> None:
        self._session_token = await self._get_session_token()
        self._http_client.set_headers(self._get_request_headers())

    async def close(self) -> None:
        try:
            url = get_item_url(self.api_url, URLs.LOGOUT)
            await self._http_client.get(url)
        except Exception:
            pass
        finally:
            await self._http_client.close()

    async def __aenter__(self) -> AsyncGLPISession:
        await self._initialize_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    # =========================================================================
    # Async API Methods
    # =========================================================================

    async def get_item(self, item_type: GlpiType, id: ResourceId, **kwargs):
        await self._initialize_session()
        url = get_item_url(self.api_url, item_type) + f"/{id}"
        kwargs = parse_kwargs(kwargs)
        return await self._http_client.get(url, params=kwargs)

    async def get_multiple_items(self, *item_keys: dict, **kwargs):
        await self._initialize_session()
        url = get_item_url(self.api_url, URLs.GET_MULTIPLE_ITEMS) + "?"
        url += "&".join(
            [
                f"items[{i}][itemtype]={item['itemtype']}&items[{i}][items_id]={item['items_id']}"
                for i, item in enumerate(item_keys)
            ]
        )
        kwargs = parse_kwargs(kwargs)
        return await self._http_client.get(url, params=kwargs)

    async def get_all_items(self, item_type: GlpiType, **kwargs):
        await self._initialize_session()
        url = get_item_url(self.api_url, item_type)
        kwargs = parse_kwargs(kwargs)
        return await self._http_client.get(url, params=kwargs)

    async def create_item(self, item_type: GlpiType, **kwargs):
        await self._initialize_session()
        url = get_item_url(self.api_url, item_type)
        body = {"input": kwargs}
        return await self._http_client.post(url, json=body)

    async def update_item(self, item_type: GlpiType, id: ResourceId, **kwargs):
        await self._initialize_session()
        url = get_item_url(self.api_url, item_type) + f"/{id}"
        body = {"input": kwargs}
        return await self._http_client.put(url, json=body)

    async def delete_item(self, item_type: GlpiType, id: ResourceId):
        await self._initialize_session()
        url = get_item_url(self.api_url, item_type) + f"/{id}"
        return await self._http_client.delete(url)

    async def create_items(self, item_type: GlpiType, *args: dict):
        await self._initialize_session()
        url = get_item_url(self.api_url, item_type)
        body = {"input": list(args)}
        return await self._http_client.post(url, json=body)

    async def get_item_search_options(self, item_type: GlpiType):
        await self._initialize_session()
        url = get_item_url(self.api_url, URLs.SEARCH_OPTIONS) + f"/{item_type}"
        return await self._http_client.get(url)

    async def search_items(self, item_type: GlpiType, criteria, **kwargs):
        await self._initialize_session()
        search_opts_resp = await self.get_item_search_options(item_type)
        search_opts: dict = search_opts_resp.json()
        criterias: list[dict] = [ev.as_dict() for ev in criteria._evaluation]

        for eval_item in criterias:
            field_ids = [
                k
                for k, v in search_opts.items()
                if isinstance(v, dict) and v.get("uid", "").lower() == eval_item["field"]
            ]
            if not field_ids:
                valid_opts = {
                    v.get("uid"): v.get("name")
                    for k, v in search_opts.items()
                    if k != "common" and isinstance(v, dict)
                }
                raise ValueError(
                    f"Couldn't find valid filtering field '{eval_item['field']}' "
                    f"for itemtype '{item_type}'. Valid options:\n\n{valid_opts}"
                )
            eval_item["field"] = field_ids[0]

        url = get_item_url(self.api_url, URLs.RESOURCE_SEARCH) + item_type + "/?"
        criteria_kwargs = [
            [f"criteria[{i}][{k}]={v}" for k, v in crit.items()] for i, crit in enumerate(criterias)
        ]

        if criteria_kwargs:
            kwargs = parse_kwargs(kwargs)
            url += "&".join(criteria_kwargs[0] + [f"{k}={v}" for k, v in kwargs.items()])

        url += "&forcedisplay[0]=2"

        return await self._http_client.get(url)

    async def download_document(self, document_id: int, **kwargs):
        await self._initialize_session()
        url = get_item_url(self.api_url, URLs.DOCUMENTS) + f"/{document_id}?alt=media"
        return await self._http_client.get(url, params=kwargs)
