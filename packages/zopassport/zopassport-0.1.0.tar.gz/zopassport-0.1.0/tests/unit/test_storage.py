"""Tests for storage adapters."""

import json
import os

import pytest

from zopassport.exceptions import ZoEncryptionError
from zopassport.storage import (
    EncryptedFileStorageAdapter,
    FileStorageAdapter,
    MemoryStorageAdapter,
)


class TestMemoryStorageAdapter:
    """Tests for MemoryStorageAdapter."""

    @pytest.mark.asyncio
    async def test_get_set_remove(self):
        """Test basic operations."""
        adapter = MemoryStorageAdapter()
        key = "test_key"
        value = "test_value"

        # Test set
        await adapter.set_item(key, value)
        assert await adapter.get_item(key) == value

        # Test remove
        await adapter.remove_item(key)
        assert await adapter.get_item(key) is None


class TestFileStorageAdapter:
    """Tests for FileStorageAdapter."""

    @pytest.fixture
    def file_path(self, tmp_path):
        return str(tmp_path / "test_session.json")

    @pytest.mark.asyncio
    async def test_save_load(self, file_path):
        """Test saving and loading from file."""
        adapter = FileStorageAdapter(file_path=file_path)
        key = "test_key"
        value = "test_value"

        await adapter.set_item(key, value)

        # Verify file content
        with open(file_path) as f:
            data = json.load(f)
            assert data[key] == value

        # Create new adapter instance to verify loading
        new_adapter = FileStorageAdapter(file_path=file_path)
        assert await new_adapter.get_item(key) == value

    @pytest.mark.asyncio
    async def test_remove_item(self, file_path):
        """Test removing item updates file."""
        adapter = FileStorageAdapter(file_path=file_path)
        key = "test_key"
        await adapter.set_item(key, "value")
        await adapter.remove_item(key)

        with open(file_path) as f:
            data = json.load(f)
            assert key not in data


class TestEncryptedFileStorageAdapter:
    """Tests for EncryptedFileStorageAdapter."""

    @pytest.fixture
    def file_path(self, tmp_path):
        return str(tmp_path / "test_session.enc")

    @pytest.fixture
    def key_file(self, tmp_path):
        return str(tmp_path / ".session_key")

    @pytest.mark.asyncio
    async def test_password_encryption(self, file_path):
        """Test encryption with password."""
        password = "secure_password"
        adapter = EncryptedFileStorageAdapter(file_path=file_path, password=password)
        key = "secret_key"
        value = "secret_value"

        await adapter.set_item(key, value)

        # Verify file is encrypted (not plain JSON)
        with open(file_path, "rb") as f:
            content = f.read()
            with pytest.raises(json.JSONDecodeError):
                json.loads(content)

        # Decrypt with same password
        new_adapter = EncryptedFileStorageAdapter(file_path=file_path, password=password)
        assert await new_adapter.get_item(key) == value

        # Fail with wrong password (actually derive different key, so decryption fails)
        with pytest.raises(ZoEncryptionError):
            EncryptedFileStorageAdapter(file_path=file_path, password="wrong_password")

    @pytest.mark.asyncio
    async def test_key_file_encryption(self, file_path, key_file):
        """Test encryption with auto-generated key file."""
        # Clean up if exists
        if os.path.exists(key_file):
            os.remove(key_file)

        adapter = EncryptedFileStorageAdapter(file_path=file_path, key_file=key_file)
        await adapter.set_item("key", "value")

        assert os.path.exists(key_file)

        # Load with same key file
        new_adapter = EncryptedFileStorageAdapter(file_path=file_path, key_file=key_file)
        assert await new_adapter.get_item("key") == "value"
