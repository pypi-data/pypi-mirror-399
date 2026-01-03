import abc
import base64
import json
import os

import aiofiles
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .exceptions import ZoEncryptionError, ZoStorageError


class StorageAdapter(abc.ABC):
    """Abstract base class for storage adapters."""

    @abc.abstractmethod
    async def get_item(self, key: str) -> str | None:
        """
        Retrieve an item from storage.

        Args:
            key: Storage key

        Returns:
            Stored value or None if not found

        Raises:
            ZoStorageError: If storage operation fails
        """
        pass

    @abc.abstractmethod
    async def set_item(self, key: str, value: str) -> None:
        """
        Store an item.

        Args:
            key: Storage key
            value: Value to store

        Raises:
            ZoStorageError: If storage operation fails
        """
        pass

    @abc.abstractmethod
    async def remove_item(self, key: str) -> None:
        """
        Remove an item from storage.

        Args:
            key: Storage key

        Raises:
            ZoStorageError: If storage operation fails
        """
        pass


class MemoryStorageAdapter(StorageAdapter):
    """In-memory storage adapter (data lost on process exit)."""

    def __init__(self) -> None:
        """Initialize in-memory storage."""
        self._store: dict[str, str] = {}

    async def get_item(self, key: str) -> str | None:
        """Get item from memory."""
        return self._store.get(key)

    async def set_item(self, key: str, value: str) -> None:
        """Set item in memory."""
        self._store[key] = value

    async def remove_item(self, key: str) -> None:
        """Remove item from memory."""
        if key in self._store:
            del self._store[key]


class FileStorageAdapter(StorageAdapter):
    """File-based storage adapter (persistent across process restarts)."""

    def __init__(self, file_path: str = "zopassport_session.json") -> None:
        """
        Initialize file storage.

        Args:
            file_path: Path to the storage file (default: zopassport_session.json)

        Raises:
            ZoStorageError: If initial file load fails
        """
        self.file_path = file_path
        self._cache: dict[str, str] = {}
        # Pre-load cache if file exists
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path) as f:
                    self._cache = json.load(f)
            except (OSError, json.JSONDecodeError) as e:
                raise ZoStorageError(
                    f"Failed to load storage file: {self.file_path}",
                    details={"error": str(e)},
                ) from e

    async def _save(self) -> None:
        """
        Save cache to file.

        Raises:
            ZoStorageError: If file write fails
        """
        try:
            async with aiofiles.open(self.file_path, "w") as f:
                await f.write(json.dumps(self._cache, indent=2))
        except OSError as e:
            raise ZoStorageError(
                f"Failed to save storage file: {self.file_path}",
                details={"error": str(e)},
            ) from e

    async def get_item(self, key: str) -> str | None:
        """Get item from file storage."""
        return self._cache.get(key)

    async def set_item(self, key: str, value: str) -> None:
        """
        Set item in file storage.

        Raises:
            ZoStorageError: If save operation fails
        """
        self._cache[key] = value
        await self._save()

    async def remove_item(self, key: str) -> None:
        """
        Remove item from file storage.

        Raises:
            ZoStorageError: If save operation fails
        """
        if key in self._cache:
            del self._cache[key]
            await self._save()


STORAGE_KEYS = {
    "ACCESS_TOKEN": "zo_access_token",
    "REFRESH_TOKEN": "zo_refresh_token",
    "TOKEN_EXPIRY": "zo_token_expiry",
    "REFRESH_EXPIRY": "zo_refresh_expiry",
    "USER": "zo_user",
    "CLIENT_DEVICE_ID": "zo_device_id",
    "CLIENT_DEVICE_SECRET": "zo_device_secret",
}


class EncryptedFileStorageAdapter(StorageAdapter):
    """
    Encrypted file-based storage adapter using Fernet (AES-128-CBC).

    Data is encrypted at rest using a key derived from a user-provided password
    or a generated key stored separately.
    """

    def __init__(
        self,
        file_path: str = "zopassport_session.enc",
        password: str | None = None,
        key_file: str | None = None,
    ) -> None:
        """
        Initialize encrypted file storage.

        Args:
            file_path: Path to the encrypted storage file (default: zopassport_session.enc)
            password: Password for encryption (if provided, key is derived from password)
            key_file: Path to key file (if password not provided, loads/generates key)

        Raises:
            ZoStorageError: If initialization fails
            ZoEncryptionError: If key generation/loading fails

        Note:
            - If neither password nor key_file is provided, a new key is generated
              and saved to ".session_key"
            - If password is provided, key is derived using PBKDF2
            - If key_file is provided, key is loaded from file
        """
        self.file_path = file_path
        self._cache: dict[str, str] = {}

        # Initialize encryption key
        if password:
            self._fernet = self._get_fernet_from_password(password)
        elif key_file:
            if os.path.exists(key_file):
                self._fernet = self._load_key_from_file(key_file)
            else:
                # Generate new key and save to the provided path
                key = Fernet.generate_key()
                self._fernet = Fernet(key)
                try:
                    with open(key_file, "wb") as f:
                        f.write(key)
                    # Set restrictive permissions (owner read/write only)
                    os.chmod(key_file, 0o600)
                except OSError as e:
                    raise ZoStorageError(
                        f"Failed to save encryption key to {key_file}",
                        details={"error": str(e)},
                    ) from e
        else:
            # Generate and save new key
            key_file = ".session_key"
            if os.path.exists(key_file):
                self._fernet = self._load_key_from_file(key_file)
            else:
                key = Fernet.generate_key()
                self._fernet = Fernet(key)
                try:
                    with open(key_file, "wb") as f:
                        f.write(key)
                    # Set restrictive permissions (owner read/write only)
                    os.chmod(key_file, 0o600)
                except OSError as e:
                    raise ZoStorageError(
                        f"Failed to save encryption key to {key_file}",
                        details={"error": str(e)},
                    ) from e

        # Load existing data if file exists
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "rb") as f:
                    encrypted_data = f.read()
                    decrypted_data = self._fernet.decrypt(encrypted_data)
                    self._cache = json.loads(decrypted_data.decode("utf-8"))
            except InvalidToken as e:
                raise ZoEncryptionError(
                    "Failed to decrypt storage file - invalid key or corrupted data",
                    details={"file_path": self.file_path},
                ) from e
            except (OSError, json.JSONDecodeError) as e:
                raise ZoStorageError(
                    f"Failed to load encrypted storage file: {self.file_path}",
                    details={"error": str(e)},
                ) from e

    def _get_fernet_from_password(self, password: str) -> Fernet:
        """
        Derive encryption key from password using PBKDF2.

        Args:
            password: User password

        Returns:
            Fernet instance

        Raises:
            ZoEncryptionError: If key derivation fails
        """
        try:
            # Use a fixed salt for deterministic key derivation
            # Note: For production, consider using a random salt stored with the data
            salt = b"zopassport_salt_v1"

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return Fernet(key)
        except Exception as e:
            raise ZoEncryptionError(
                "Failed to derive encryption key from password",
                details={"error": str(e)},
            ) from e

    def _load_key_from_file(self, key_file: str) -> Fernet:
        """
        Load encryption key from file.

        Args:
            key_file: Path to key file

        Returns:
            Fernet instance

        Raises:
            ZoEncryptionError: If key loading fails
        """
        try:
            with open(key_file, "rb") as f:
                key = f.read()
            return Fernet(key)
        except OSError as e:
            raise ZoEncryptionError(
                f"Failed to load encryption key from {key_file}",
                details={"error": str(e)},
            ) from e
        except Exception as e:
            raise ZoEncryptionError(
                f"Invalid encryption key in {key_file}",
                details={"error": str(e)},
            ) from e

    async def _save(self) -> None:
        """
        Encrypt and save cache to file.

        Raises:
            ZoStorageError: If file write fails
            ZoEncryptionError: If encryption fails
        """
        try:
            # Serialize to JSON
            json_data = json.dumps(self._cache, indent=2)

            # Encrypt
            encrypted_data = self._fernet.encrypt(json_data.encode("utf-8"))

            # Write to file
            async with aiofiles.open(self.file_path, "wb") as f:
                await f.write(encrypted_data)

            # Set restrictive permissions (owner read/write only)
            os.chmod(self.file_path, 0o600)

        except InvalidToken as e:
            raise ZoEncryptionError(
                "Failed to encrypt data",
                details={"file_path": self.file_path},
            ) from e
        except OSError as e:
            raise ZoStorageError(
                f"Failed to save encrypted storage file: {self.file_path}",
                details={"error": str(e)},
            ) from e

    async def get_item(self, key: str) -> str | None:
        """Get item from encrypted storage."""
        return self._cache.get(key)

    async def set_item(self, key: str, value: str) -> None:
        """
        Set item in encrypted storage.

        Raises:
            ZoStorageError: If save operation fails
            ZoEncryptionError: If encryption fails
        """
        self._cache[key] = value
        await self._save()

    async def remove_item(self, key: str) -> None:
        """
        Remove item from encrypted storage.

        Raises:
            ZoStorageError: If save operation fails
            ZoEncryptionError: If encryption fails
        """
        if key in self._cache:
            del self._cache[key]
            await self._save()
