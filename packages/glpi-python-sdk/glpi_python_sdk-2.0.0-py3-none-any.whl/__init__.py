"""GLPI Python SDK - Modern Python library for GLPI REST API."""

__version__ = "2.0.0"

# Core imports (explicit re-exports for module access)
from . import connection as connection
from . import exceptions as exceptions
from . import helpers as helpers
from . import http_client as http_client
from . import models as models
from . import resources as resources

# Convenience imports
from .connection import AsyncGLPISession, GLPISession, URLs
from .exceptions import (
    AuthenticationError,
    # Aliases for compatibility
    AuthError,
    ConnectionError,
    FileUploadError,
    ForbiddenError,
    GLPIError,
    InvalidCredentialsError,
    ItemCreationError,
    ItemDoesNotExistError,
    ItemDoesNotExists,
    NetworkError,
    ResourceError,
    ResourceNotFoundError,
    SessionTokenError,
    TimeoutError,
    Unauthorized,
    UnauthorizedError,
    ValidationError,
)
from .http_client import AsyncHTTPClient, ClientConfig, HTTPClient
from .models import FilterCriteria, GLPIItem, ItemList, Resource

__all__ = [
    # Version
    "__version__",
    # Sessions
    "GLPISession",
    "AsyncGLPISession",
    # HTTP Client
    "ClientConfig",
    "HTTPClient",
    "AsyncHTTPClient",
    # Models
    "GLPIItem",
    "Resource",
    "FilterCriteria",
    "ItemList",
    # URLs
    "URLs",
    # Exceptions
    "GLPIError",
    "AuthenticationError",
    "InvalidCredentialsError",
    "SessionTokenError",
    "UnauthorizedError",
    "ForbiddenError",
    "NetworkError",
    "ConnectionError",
    "TimeoutError",
    "ResourceError",
    "ResourceNotFoundError",
    "ItemDoesNotExistError",
    "ItemCreationError",
    "ValidationError",
    "FileUploadError",
    # Legacy aliases
    "AuthError",
    "ItemDoesNotExists",
    "Unauthorized",
]
