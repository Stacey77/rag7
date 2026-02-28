"""HashiCorp Vault integration adapter."""
from __future__ import annotations
import base64
import hashlib
import logging
import secrets
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

@dataclass
class Secret:
    path: str = ""
    data: Dict[str, str] = field(default_factory=dict)
    version: int = 1
    lease_duration: int = 3600
    renewable: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

@dataclass
class VaultToken:
    token_id: str = field(default_factory=lambda: secrets.token_hex(16))
    policies: List[str] = field(default_factory=list)
    renewable: bool = True
    ttl_seconds: int = 3600
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.created_at + timedelta(seconds=self.ttl_seconds)

class VaultACL:
    def __init__(self) -> None:
        self._policies: Dict[str, Dict[str, List[str]]] = {
            "admin": {"*": ["read", "write", "delete", "list"]},
            "readonly": {"*": ["read", "list"]},
            "appuser": {"secret/app/*": ["read"], "secret/db/*": ["read"]},
        }

    def check_permission(self, token: VaultToken, path: str, operation: str) -> bool:
        for policy in token.policies:
            rules = self._policies.get(policy, {})
            for pattern, ops in rules.items():
                if pattern == "*" or path.startswith(pattern.rstrip("*")):
                    if operation in ops:
                        return True
        return False

    def add_policy(self, name: str, rules: Dict[str, List[str]]) -> None:
        self._policies[name] = rules

class VaultIntegration:
    """Simulated HashiCorp Vault for secrets management."""

    def __init__(self, address: str = "http://localhost:8200") -> None:
        self.address = address
        self._secrets: Dict[str, List[Secret]] = {}  # path -> versions
        self._tokens: Dict[str, VaultToken] = {}
        self._acl = VaultACL()
        self._audit_log: List[Dict[str, Any]] = []
        self._root_token = self._bootstrap_root_token()
        logger.info("VaultIntegration initialized (addr=%s)", address)

    def _bootstrap_root_token(self) -> VaultToken:
        token = VaultToken(policies=["admin"], ttl_seconds=86400 * 365)
        self._tokens[token.token_id] = token
        return token

    @property
    def root_token(self) -> str:
        return self._root_token.token_id

    def create_token(self, policies: List[str], ttl_seconds: int = 3600) -> VaultToken:
        token = VaultToken(policies=policies, ttl_seconds=ttl_seconds)
        self._tokens[token.token_id] = token
        logger.debug("Created token with policies: %s", policies)
        return token

    def revoke_token(self, token_id: str) -> bool:
        return bool(self._tokens.pop(token_id, None))

    def _get_token(self, token_id: str) -> Optional[VaultToken]:
        token = self._tokens.get(token_id)
        if token and token.is_expired:
            del self._tokens[token_id]
            return None
        return token

    def _audit(self, operation: str, path: str, token_id: str) -> None:
        self._audit_log.append({
            "operation": operation, "path": path,
            "token": token_id[:8] + "...", "timestamp": datetime.utcnow().isoformat(),
        })

    def write_secret(self, path: str, data: Dict[str, str],
                      token_id: Optional[str] = None) -> Optional[Secret]:
        tok_id = token_id or self._root_token.token_id
        token = self._get_token(tok_id)
        if not token or not self._acl.check_permission(token, path, "write"):
            logger.warning("Write denied for path '%s'", path)
            return None
        versions = self._secrets.setdefault(path, [])
        version = len(versions) + 1
        secret = Secret(path=path, data=dict(data), version=version,
                        expires_at=datetime.utcnow() + timedelta(hours=24))
        versions.append(secret)
        self._audit("write", path, tok_id)
        logger.debug("Written secret at '%s' (v%d)", path, version)
        return secret

    def read_secret(self, path: str, version: Optional[int] = None,
                     token_id: Optional[str] = None) -> Optional[Secret]:
        tok_id = token_id or self._root_token.token_id
        token = self._get_token(tok_id)
        if not token or not self._acl.check_permission(token, path, "read"):
            logger.warning("Read denied for path '%s'", path)
            return None
        versions = self._secrets.get(path, [])
        if not versions:
            return None
        secret = versions[version - 1] if version and version <= len(versions) else versions[-1]
        self._audit("read", path, tok_id)
        return secret

    def delete_secret(self, path: str, token_id: Optional[str] = None) -> bool:
        tok_id = token_id or self._root_token.token_id
        token = self._get_token(tok_id)
        if not token or not self._acl.check_permission(token, path, "delete"):
            return False
        existed = bool(self._secrets.pop(path, None))
        if existed:
            self._audit("delete", path, tok_id)
        return existed

    def list_secrets(self, prefix: str, token_id: Optional[str] = None) -> List[str]:
        tok_id = token_id or self._root_token.token_id
        token = self._get_token(tok_id)
        if not token:
            return []
        return [p for p in self._secrets if p.startswith(prefix)]

    def rotate_secret(self, path: str, new_data: Dict[str, str],
                       token_id: Optional[str] = None) -> Optional[Secret]:
        return self.write_secret(path, new_data, token_id)

    def get_audit_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._audit_log[-limit:]
