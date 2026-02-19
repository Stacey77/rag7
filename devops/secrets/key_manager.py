"""Cryptographic key management."""
from __future__ import annotations
import base64
import hashlib
import logging
import os
import secrets
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

@dataclass
class CryptoKey:
    key_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    key_type: str = "symmetric"   # symmetric | rsa | ecdsa | hmac
    algorithm: str = "AES-256"
    purpose: str = "encryption"   # encryption | signing | authentication
    key_material: Optional[bytes] = None
    status: str = "active"        # active | inactive | pending_deletion
    rotation_policy_days: int = 90
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    last_rotated: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_expired(self) -> bool:
        return self.expires_at is not None and datetime.utcnow() > self.expires_at

    @property
    def rotation_due(self) -> bool:
        ref = self.last_rotated or self.created_at
        return (datetime.utcnow() - ref).days >= self.rotation_policy_days


def _generate_symmetric_key(bits: int = 256) -> bytes:
    return secrets.token_bytes(bits // 8)


def _derive_key(password: str, salt: Optional[bytes] = None, iterations: int = 100000) -> tuple:
    if salt is None:
        salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations, dklen=32)
    return dk, salt


def _hmac_sign(key_material: bytes, data: bytes) -> bytes:
    import hmac
    return hmac.new(key_material, data, hashlib.sha256).digest()


def _simple_encrypt(key_material: bytes, plaintext: str) -> str:
    """XOR-based encryption for simulation (not production-safe)."""
    data = plaintext.encode()
    key_stream = (key_material * (len(data) // len(key_material) + 1))[:len(data)]
    encrypted = bytes(d ^ k for d, k in zip(data, key_stream))
    return base64.b64encode(encrypted).decode()


def _simple_decrypt(key_material: bytes, ciphertext: str) -> str:
    data = base64.b64decode(ciphertext)
    key_stream = (key_material * (len(data) // len(key_material) + 1))[:len(data)]
    decrypted = bytes(d ^ k for d, k in zip(data, key_stream))
    return decrypted.decode()


class KeyManager:
    """
    Cryptographic key lifecycle management with rotation,
    encryption/decryption, signing, and key derivation.
    """

    def __init__(self) -> None:
        self._keys: Dict[str, CryptoKey] = {}
        self._key_aliases: Dict[str, str] = {}  # alias -> key_id
        self._rotation_history: List[Dict[str, Any]] = []
        logger.info("KeyManager initialized")

    def create_key(self, alias: str, key_type: str = "symmetric",
                    algorithm: str = "AES-256", purpose: str = "encryption",
                    rotation_policy_days: int = 90,
                    ttl_days: Optional[int] = None) -> CryptoKey:
        key_material = _generate_symmetric_key()
        expires_at = datetime.utcnow() + timedelta(days=ttl_days) if ttl_days else None
        key = CryptoKey(key_type=key_type, algorithm=algorithm, purpose=purpose,
                        key_material=key_material, rotation_policy_days=rotation_policy_days,
                        expires_at=expires_at)
        self._keys[key.key_id] = key
        self._key_aliases[alias] = key.key_id
        logger.info("Created key '%s' (type=%s, algo=%s)", alias, key_type, algorithm)
        return key

    def get_key(self, key_id_or_alias: str) -> Optional[CryptoKey]:
        key_id = self._key_aliases.get(key_id_or_alias, key_id_or_alias)
        return self._keys.get(key_id)

    def rotate_key(self, alias: str) -> CryptoKey:
        old_key = self.get_key(alias)
        new_material = _generate_symmetric_key()
        new_key = CryptoKey(
            key_type=old_key.key_type if old_key else "symmetric",
            algorithm=old_key.algorithm if old_key else "AES-256",
            purpose=old_key.purpose if old_key else "encryption",
            key_material=new_material,
            rotation_policy_days=old_key.rotation_policy_days if old_key else 90,
            last_rotated=datetime.utcnow(),
        )
        if old_key:
            old_key.status = "inactive"
            self._rotation_history.append({
                "alias": alias, "old_key_id": old_key.key_id,
                "new_key_id": new_key.key_id, "rotated_at": datetime.utcnow().isoformat(),
            })
        self._keys[new_key.key_id] = new_key
        self._key_aliases[alias] = new_key.key_id
        logger.info("Rotated key '%s'", alias)
        return new_key

    def encrypt(self, alias: str, plaintext: str) -> Optional[str]:
        key = self.get_key(alias)
        if not key or not key.key_material or key.is_expired:
            return None
        return _simple_encrypt(key.key_material, plaintext)

    def decrypt(self, alias: str, ciphertext: str) -> Optional[str]:
        key = self.get_key(alias)
        if not key or not key.key_material:
            return None
        try:
            return _simple_decrypt(key.key_material, ciphertext)
        except Exception as exc:
            logger.error("Decryption failed: %s", exc)
            return None

    def sign(self, alias: str, data: str) -> Optional[str]:
        key = self.get_key(alias)
        if not key or not key.key_material:
            return None
        sig = _hmac_sign(key.key_material, data.encode())
        return base64.b64encode(sig).decode()

    def verify(self, alias: str, data: str, signature: str) -> bool:
        expected = self.sign(alias, data)
        return expected == signature if expected else False

    def derive_key(self, password: str, salt: Optional[str] = None) -> tuple:
        salt_bytes = base64.b64decode(salt) if salt else None
        dk, salt_bytes = _derive_key(password, salt_bytes)
        return base64.b64encode(dk).decode(), base64.b64encode(salt_bytes).decode()

    def check_rotation_needed(self) -> List[str]:
        return [alias for alias, kid in self._key_aliases.items()
                if (k := self._keys.get(kid)) and k.rotation_due]

    def revoke_key(self, alias: str) -> bool:
        key = self.get_key(alias)
        if not key:
            return False
        key.status = "inactive"
        return True

    def list_keys(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        result = []
        for alias, kid in self._key_aliases.items():
            key = self._keys.get(kid)
            if key and (status is None or key.status == status):
                result.append({"alias": alias, "key_id": kid, "type": key.key_type,
                                "status": key.status, "rotation_due": key.rotation_due})
        return result
