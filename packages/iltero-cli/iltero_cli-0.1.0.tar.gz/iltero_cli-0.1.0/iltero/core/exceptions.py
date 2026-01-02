"""Custom exceptions for Iltero CLI."""


class IlteroError(Exception):
    """Base exception for all Iltero CLI errors."""

    def __init__(self, message: str, exit_code: int = 1):
        self.message = message
        self.exit_code = exit_code
        super().__init__(message)


class AuthenticationError(IlteroError):
    """Authentication-related errors."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, exit_code=2)


class ConfigurationError(IlteroError):
    """Configuration-related errors."""

    def __init__(self, message: str):
        super().__init__(message, exit_code=3)


class APIError(IlteroError):
    """Backend API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message, exit_code=4)


class ValidationError(IlteroError):
    """Input validation errors."""

    def __init__(self, message: str):
        super().__init__(message, exit_code=5)


class ResourceNotFoundError(IlteroError):
    """Resource not found errors."""

    def __init__(self, resource_type: str, identifier: str):
        message = f"{resource_type} not found: {identifier}"
        super().__init__(message, exit_code=6)


class ScannerError(IlteroError):
    """Scanner execution errors."""

    def __init__(self, scanner_name: str, message: str):
        full_message = f"Scanner '{scanner_name}' error: {message}"
        super().__init__(full_message, exit_code=7)


class RateLimitError(IlteroError):
    """Rate limit exceeded errors."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, exit_code=8)


class NetworkError(IlteroError):
    """Network connectivity errors."""

    def __init__(self, message: str = "Network error"):
        super().__init__(message, exit_code=9)
