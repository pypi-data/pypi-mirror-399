"""
Pytest configuration and shared fixtures for ZoPassport SDK tests.
"""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio

from zopassport import ZoPassportConfig, ZoPassportSDK
from zopassport.client import ZoApiClient
from zopassport.storage import MemoryStorageAdapter

# Configure pytest-asyncio
pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client_key() -> str:
    """Fixture for test client key."""
    return "test_client_key_12345"


@pytest.fixture
def mock_user_data() -> dict[str, Any]:
    """Fixture for mock user data."""
    return {
        "id": "user_123",
        "first_name": "John",
        "last_name": "Doe",
        "email_address": "john@example.com",
        "mobile_country_code": "91",
        "mobile_number": "9876543210",
        "wallet_address": "0x1234567890abcdef",
        "bio": "Test user",
    }


@pytest.fixture
def mock_auth_response(mock_user_data: dict[str, Any]) -> dict[str, Any]:
    """Fixture for mock authentication response."""
    return {
        "user": mock_user_data,
        "access_token": "mock_access_token",
        "refresh_token": "mock_refresh_token",
        "access_token_expiry": "2025-12-31T23:59:59Z",
        "refresh_token_expiry": "2026-12-31T23:59:59Z",
        "device_id": "web-1234567890-abc123",
        "device_secret": "mock_device_secret",
    }


@pytest.fixture
def mock_storage():
    """Fixture for in-memory storage adapter."""
    return MemoryStorageAdapter()


@pytest_asyncio.fixture
async def api_client(client_key: str, mock_storage: MemoryStorageAdapter) -> AsyncGenerator:
    """Fixture for API client with mock storage."""
    config = ZoPassportConfig(
        client_key=client_key,
        base_url="https://api.test.zo.xyz",
        storage_adapter=mock_storage,
    )
    client = ZoApiClient(config)
    yield client
    await client.close()


@pytest_asyncio.fixture
async def sdk(client_key: str, mock_storage: MemoryStorageAdapter) -> AsyncGenerator:
    """Fixture for SDK instance with mock storage."""
    sdk_instance = ZoPassportSDK(
        client_key=client_key,
        base_url="https://api.test.zo.xyz",
        storage_adapter=mock_storage,
        auto_refresh=False,  # Disable auto-refresh for tests
        debug=True,
    )
    await sdk_instance.initialize()
    yield sdk_instance
    await sdk_instance.close()


@pytest.fixture
def mock_httpx_response():
    """Fixture for creating mock httpx responses."""

    def _create_response(
        status_code: int = 200,
        json_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Mock:
        response = Mock()
        response.status_code = status_code
        response.headers = headers or {}
        response.json = Mock(return_value=json_data or {})
        return response

    return _create_response


@pytest.fixture
def mock_client():
    """Fixture for a mock API client."""
    client = AsyncMock()
    client.request = AsyncMock()
    return client
