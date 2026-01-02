"""Tests for core exceptions."""

from iltero.core.exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    IlteroError,
    ResourceNotFoundError,
    ScannerError,
    ValidationError,
)


def test_iltero_error():
    """Test base IlteroError."""
    error = IlteroError("Test error", exit_code=42)
    assert str(error) == "Test error"
    assert error.message == "Test error"
    assert error.exit_code == 42


def test_authentication_error():
    """Test AuthenticationError."""
    error = AuthenticationError("Auth failed")
    assert str(error) == "Auth failed"
    assert error.exit_code == 2


def test_configuration_error():
    """Test ConfigurationError."""
    error = ConfigurationError("Config invalid")
    assert str(error) == "Config invalid"
    assert error.exit_code == 3


def test_api_error():
    """Test APIError."""
    error = APIError("API failed", status_code=404)
    assert str(error) == "API failed"
    assert error.status_code == 404
    assert error.exit_code == 4


def test_validation_error():
    """Test ValidationError."""
    error = ValidationError("Invalid input")
    assert str(error) == "Invalid input"
    assert error.exit_code == 5


def test_resource_not_found_error():
    """Test ResourceNotFoundError."""
    error = ResourceNotFoundError("Stack", "abc123")
    assert "Stack not found: abc123" in str(error)
    assert error.exit_code == 6


def test_scanner_error():
    """Test ScannerError."""
    error = ScannerError("checkov", "Failed to run")
    assert "Scanner 'checkov' error: Failed to run" in str(error)
    assert error.exit_code == 7
