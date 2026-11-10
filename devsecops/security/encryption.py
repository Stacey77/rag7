"""Data encryption and decryption using Fernet symmetric encryption."""

from __future__ import annotations

import base64
import os
from typing import Any

from loguru import logger

# Try to import the cryptography library; fall back to abstract stubs if unavailable.
try:
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    _CRYPTOGRAPHY_AVAILABLE = True
except ImportError:  # pragma: no cover
    _CRYPTOGRAPHY_AVAILABLE = False


class EncryptionError(Exception):
    """Raised when encryption or decryption fails."""


class Encryption:
    """Symmetric data encryption using Fernet (AES-128-CBC + HMAC-SHA256).

    When the ``cryptography`` package is not installed, the class falls
    back to an abstract interface that raises :class:`EncryptionError`
    with a clear installation message rather than silently failing.

    Encryption keys are never hard-coded; they are generated at runtime
    or derived from a passphrase and salt read from the environment.

    Attributes:
        _fernet: Fernet cipher instance (``None`` when library unavailable).
    """

    def __init__(self, key: bytes | None = None) -> None:
        """Initialise the encryption engine.

        If no ``key`` is provided, a new random 32-byte key is generated.
        To use a persistent key, pass the bytes of a stored Fernet key.

        Args:
            key: Optional Fernet-compatible 32-byte base64url key.
                 Generate with :meth:`generate_key`.

        Raises:
            EncryptionError: If ``cryptography`` is unavailable and
                any encryption/decryption operation is attempted.
        """
        self._fernet: Any = None

        if not _CRYPTOGRAPHY_AVAILABLE:
            logger.warning(
                "cryptography package not installed. "
                "Encryption operations will raise EncryptionError. "
                "Install with: pip install cryptography"
            )
            return

        if key is None:
            key = Fernet.generate_key()

        try:
            self._fernet = Fernet(key)
        except Exception as exc:
            raise EncryptionError(f"Invalid Fernet key: {exc}") from exc

        logger.info("Encryption engine initialised (cryptography library available)")

    @staticmethod
    def generate_key() -> bytes:
        """Generate a new random Fernet encryption key.

        Returns:
            URL-safe base64-encoded 32-byte key.

        Raises:
            EncryptionError: If ``cryptography`` is unavailable.
        """
        if not _CRYPTOGRAPHY_AVAILABLE:
            raise EncryptionError(
                "cryptography package required. Install with: pip install cryptography"
            )
        return Fernet.generate_key()

    @staticmethod
    def derive_key(passphrase: str, salt: bytes | None = None) -> tuple[bytes, bytes]:
        """Derive a Fernet key from a passphrase using PBKDF2-HMAC-SHA256.

        Args:
            passphrase: Human-memorable passphrase.
            salt: Optional 16-byte salt; generated randomly if ``None``.

        Returns:
            Tuple of ``(key, salt)`` where key is Fernet-compatible.

        Raises:
            EncryptionError: If ``cryptography`` is unavailable.
        """
        if not _CRYPTOGRAPHY_AVAILABLE:
            raise EncryptionError(
                "cryptography package required. Install with: pip install cryptography"
            )

        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480_000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
        return key, salt

    def encrypt(self, plaintext: bytes) -> bytes:
        """Encrypt plaintext bytes.

        Args:
            plaintext: Data to encrypt.

        Returns:
            Fernet token (encrypted ciphertext).

        Raises:
            EncryptionError: If ``cryptography`` is unavailable or
                encryption fails.
        """
        self._assert_available()
        try:
            return self._fernet.encrypt(plaintext)
        except Exception as exc:
            raise EncryptionError(f"Encryption failed: {exc}") from exc

    def encrypt_text(self, text: str, encoding: str = "utf-8") -> bytes:
        """Encrypt a unicode string.

        Args:
            text: String to encrypt.
            encoding: Character encoding.

        Returns:
            Fernet token bytes.

        Raises:
            EncryptionError: If encryption fails.
        """
        return self.encrypt(text.encode(encoding))

    def decrypt(self, token: bytes) -> bytes:
        """Decrypt a Fernet token.

        Args:
            token: Encrypted Fernet token.

        Returns:
            Decrypted plaintext bytes.

        Raises:
            EncryptionError: If decryption fails (bad key or tampered data).
        """
        self._assert_available()
        try:
            return self._fernet.decrypt(token)
        except InvalidToken as exc:
            raise EncryptionError("Decryption failed: invalid token or wrong key") from exc
        except Exception as exc:
            raise EncryptionError(f"Decryption failed: {exc}") from exc

    def decrypt_text(self, token: bytes, encoding: str = "utf-8") -> str:
        """Decrypt a Fernet token to a unicode string.

        Args:
            token: Encrypted Fernet token.
            encoding: Character encoding.

        Returns:
            Decrypted string.

        Raises:
            EncryptionError: If decryption fails.
        """
        return self.decrypt(token).decode(encoding)

    def rotate_key(self, new_key: bytes) -> None:
        """Replace the current encryption key.

        Existing tokens encrypted with the old key will no longer be
        decryptable after rotation unless you re-encrypt them first.

        Args:
            new_key: New Fernet-compatible key.

        Raises:
            EncryptionError: If the new key is invalid.
        """
        self._assert_available()
        try:
            self._fernet = Fernet(new_key)
            logger.info("Encryption key rotated")
        except Exception as exc:
            raise EncryptionError(f"Key rotation failed: {exc}") from exc

    def _assert_available(self) -> None:
        """Raise EncryptionError if the cryptography library is unavailable.

        Raises:
            EncryptionError: If ``cryptography`` is not installed.
        """
        if not _CRYPTOGRAPHY_AVAILABLE:
            raise EncryptionError(
                "cryptography package required. Install with: pip install cryptography"
            )
        if self._fernet is None:
            raise EncryptionError("Encryption engine not initialised")

    @property
    def is_available(self) -> bool:
        """Whether the cryptography library is available and engine is ready."""
        return _CRYPTOGRAPHY_AVAILABLE and self._fernet is not None
