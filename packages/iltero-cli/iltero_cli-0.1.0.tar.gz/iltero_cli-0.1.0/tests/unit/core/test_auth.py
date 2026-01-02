"""Tests for AuthManager."""

import pytest

from iltero.core.auth import AuthManager
from iltero.core.config import ConfigManager
from iltero.core.exceptions import AuthenticationError


@pytest.fixture
def mock_keyring(monkeypatch):
    """Mock keyring module."""
    stored_password = None

    def mock_get_password(service, username):
        return stored_password

    def mock_set_password(service, username, password):
        nonlocal stored_password
        stored_password = password

    def mock_delete_password(service, username):
        nonlocal stored_password
        if stored_password is None:
            import keyring.errors

            raise keyring.errors.PasswordDeleteError()
        stored_password = None

    monkeypatch.setattr("keyring.get_password", mock_get_password)
    monkeypatch.setattr("keyring.set_password", mock_set_password)
    monkeypatch.setattr("keyring.delete_password", mock_delete_password)

    return stored_password


def test_set_token_valid(mock_keyring):
    """Test setting a valid token."""
    config = ConfigManager()
    auth = AuthManager(config)

    auth.set_token("itk_u_test123")
    token = auth.get_token()
    assert token == "itk_u_test123"


def test_set_token_invalid_format(mock_keyring):
    """Test setting token with invalid format."""
    config = ConfigManager()
    auth = AuthManager(config)

    with pytest.raises(AuthenticationError, match="Invalid token format"):
        auth.set_token("invalid_token")


def test_set_token_empty(mock_keyring):
    """Test setting empty token."""
    config = ConfigManager()
    auth = AuthManager(config)

    with pytest.raises(AuthenticationError, match="Token cannot be empty"):
        auth.set_token("")


def test_get_token_not_found(mock_keyring):
    """Test getting token when not configured."""
    config = ConfigManager()
    auth = AuthManager(config)

    with pytest.raises(AuthenticationError, match="No API token found"):
        auth.get_token()


def test_env_var_token_precedence(mock_keyring, monkeypatch):
    """Test that env var token takes precedence over keyring."""
    monkeypatch.setenv("ILTERO_TOKEN", "itk_p_env_token")

    config = ConfigManager()
    auth = AuthManager(config)

    # Set keyring token
    auth.set_token("itk_u_keyring_token")

    # Env var should take precedence
    assert auth.get_token() == "itk_p_env_token"


def test_clear_token(mock_keyring):
    """Test clearing token."""
    config = ConfigManager()
    auth = AuthManager(config)

    auth.set_token("itk_u_test123")
    assert auth.has_token()

    auth.clear_token()
    assert not auth.has_token()


def test_has_token(mock_keyring):
    """Test has_token method."""
    config = ConfigManager()
    auth = AuthManager(config)

    assert not auth.has_token()

    auth.set_token("itk_u_test123")
    assert auth.has_token()
