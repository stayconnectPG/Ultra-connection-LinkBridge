"""Tests for the relay token manager."""

import pytest

from relay.authentication.token import TokenManager, TokenPayload


@pytest.fixture
def token_manager() -> TokenManager:
    return TokenManager(secret="test-secret-key-for-testing")


def test_register_device(token_manager: TokenManager) -> None:
    ok, token, err = token_manager.register_device(
        "debian-001", "server", "debian", "key-pem-data"
    )
    assert ok
    assert token
    assert err is None


def test_register_duplicate_device(token_manager: TokenManager) -> None:
    token_manager.register_device("debian-001", "server", "debian")
    ok, token, err = token_manager.register_device("debian-001", "server", "debian")
    assert not ok
    assert err == "Device already registered"


def test_access_token_validation(token_manager: TokenManager) -> None:
    _, token, _ = token_manager.register_device("android-001", "android", "android")
    payload = token_manager.validate_access_token(token)
    assert payload is not None
    assert payload.device_id == "android-001"
    assert payload.kind == "access"


def test_session_token_validation(token_manager: TokenManager) -> None:
    token = token_manager.issue_session_token("debian-001", "android-001")
    payload = token_manager.validate_session_token(token)
    assert payload is not None
    assert payload.kind == "session"
    assert payload.device_id == "debian-001"
    assert payload.paired_device_id == "android-001"


def test_cross_token_rejected(token_manager: TokenManager) -> None:
    access_token = token_manager.register_device("debian-001", "server", "debian")[1]
    assert token_manager.validate_session_token(access_token) is None
    session_token = token_manager.issue_session_token("debian-001")
    assert token_manager.validate_access_token(session_token) is None


def test_invalid_token_rejected(token_manager: TokenManager) -> None:
    assert token_manager.validate_access_token("invalid.token.here") is None
    assert token_manager.validate_session_token("") is None
