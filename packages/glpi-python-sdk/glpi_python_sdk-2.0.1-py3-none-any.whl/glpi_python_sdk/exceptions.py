"""
GLPI Python SDK - Custom Exceptions

Exceptions organized by category for easier error handling.
Compatible with FastAPI and async contexts.
"""

from typing import Any


class GLPIError(Exception):
    """Base exception for all GLPI library errors."""

    def __init__(self, message: str, details: Any = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


# =============================================================================
# Authentication Errors
# =============================================================================


class AuthenticationError(GLPIError):
    """Base for authentication errors."""

    pass


class InvalidCredentialsError(AuthenticationError):
    """Invalid credentials (user/password or token)."""

    def __init__(self, message: str = "Invalid credentials provided", details: Any = None):
        super().__init__(message, details)


class SessionTokenError(AuthenticationError):
    """Failed to obtain or renew session token."""

    def __init__(self, message: str = "Failed to obtain session token", details: Any = None):
        super().__init__(message, details)


class UnauthorizedError(AuthenticationError):
    """HTTP 401 - Unauthorized."""

    def __init__(self, message: str = "Unauthorized access", details: Any = None):
        super().__init__(message, details)


class ForbiddenError(AuthenticationError):
    """HTTP 403 - Forbidden."""

    def __init__(self, message: str = "Access forbidden", details: Any = None):
        super().__init__(message, details)


# =============================================================================
# Network Errors
# =============================================================================


class NetworkError(GLPIError):
    """Base for network/connection errors."""

    pass


class ConnectionError(NetworkError):
    """Failed to connect to GLPI server."""

    def __init__(self, message: str = "Failed to connect to GLPI server", details: Any = None):
        super().__init__(message, details)


class TimeoutError(NetworkError):
    """Request timeout."""

    def __init__(self, message: str = "Request timed out", details: Any = None):
        super().__init__(message, details)


class ServerError(NetworkError):
    """HTTP 5xx server error."""

    def __init__(self, message: str = "Server error", status_code: int = 500, details: Any = None):
        self.status_code = status_code
        super().__init__(f"{message} (HTTP {status_code})", details)


# =============================================================================
# Resource Errors
# =============================================================================


class ResourceError(GLPIError):
    """Base for GLPI resource-related errors."""

    pass


class ResourceNotFoundError(ResourceError):
    """Item/Resource not found (404 or ERROR_RESOURCE_NOT_FOUND_NOR_COMMONDBTM)."""

    def __init__(
        self,
        resource_type: str = None,
        resource_id: int = None,
        message: str = None,
        details: Any = None,
    ):
        self.resource_type = resource_type
        self.resource_id = resource_id
        if message is None:
            if resource_type and resource_id:
                message = f"{resource_type} with id {resource_id} not found"
            elif resource_type:
                message = f"{resource_type} not found"
            else:
                message = "Resource not found"
        super().__init__(message, details)


class ItemDoesNotExistError(ResourceNotFoundError):
    """Alias for compatibility - item does not exist."""

    pass


class MultipleResultsError(ResourceError):
    """GET operation returned multiple results when expecting one."""

    def __init__(self, message: str = "Expected single result, got multiple", details: Any = None):
        super().__init__(message, details)


class ItemCreationError(ResourceError):
    """Failed to create item."""

    def __init__(self, resource_type: str = None, message: str = None, details: Any = None):
        self.resource_type = resource_type
        if message is None:
            message = (
                f"Failed to create {resource_type}" if resource_type else "Failed to create item"
            )
        super().__init__(message, details)


class ItemUpdateError(ResourceError):
    """Failed to update item."""

    def __init__(
        self,
        resource_type: str = None,
        resource_id: int = None,
        message: str = None,
        details: Any = None,
    ):
        self.resource_type = resource_type
        self.resource_id = resource_id
        if message is None:
            message = (
                f"Failed to update {resource_type} {resource_id}"
                if resource_type
                else "Failed to update item"
            )
        super().__init__(message, details)


class ItemDeletionError(ResourceError):
    """Failed to delete item."""

    def __init__(
        self,
        resource_type: str = None,
        resource_id: int = None,
        message: str = None,
        details: Any = None,
    ):
        self.resource_type = resource_type
        self.resource_id = resource_id
        if message is None:
            message = (
                f"Failed to delete {resource_type} {resource_id}"
                if resource_type
                else "Failed to delete item"
            )
        super().__init__(message, details)


# =============================================================================
# Validation Errors
# =============================================================================


class ValidationError(GLPIError):
    """Data/configuration validation error."""

    def __init__(self, message: str = "Validation error", field: str = None, details: Any = None):
        self.field = field
        super().__init__(message, details)


class ConfigurationError(ValidationError):
    """Library configuration error."""

    def __init__(self, message: str = "Configuration error", details: Any = None):
        super().__init__(message, details=details)


class SearchCriteriaError(ValidationError):
    """Search criteria error."""

    def __init__(
        self,
        field: str = None,
        message: str = None,
        valid_options: dict = None,
        details: Any = None,
    ):
        self.valid_options = valid_options
        if message is None:
            message = (
                f"Invalid search criteria field: {field}" if field else "Invalid search criteria"
            )
        super().__init__(message, field=field, details=details)


# =============================================================================
# File/Document Errors
# =============================================================================


class FileError(GLPIError):
    """Base for file errors."""

    pass


class FileUploadError(FileError):
    """File upload failed."""

    def __init__(self, filename: str = None, message: str = None, details: Any = None):
        self.filename = filename
        if message is None:
            message = f"Failed to upload file: {filename}" if filename else "Failed to upload file"
        super().__init__(message, details)


class FileDownloadError(FileError):
    """File download failed."""

    def __init__(self, document_id: int = None, message: str = None, details: Any = None):
        self.document_id = document_id
        if message is None:
            message = (
                f"Failed to download document {document_id}"
                if document_id
                else "Failed to download file"
            )
        super().__init__(message, details)


# =============================================================================
# Aliases for legacy code compatibility
# =============================================================================

# Keep old names working
AuthError = SessionTokenError
ItemDoesNotExists = ItemDoesNotExistError
Unauthorized = UnauthorizedError
ResourceNotFound = ResourceNotFoundError
MultipleGetResult = MultipleResultsError
