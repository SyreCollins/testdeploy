import hashlib
import hmac
import secrets
import time
from collections import OrderedDict
from datetime import UTC, datetime
from typing import Any

API_KEY_PREFIX = "zam_"


class ApiKeyStore:
    _keys: OrderedDict[str, dict[str, Any]] = OrderedDict()
    _max_keys = 100
    _bootstrapped = False

    def bootstrap_static_keys(self, raw_keys: list[str]) -> None:
        if self._bootstrapped:
            return
        for raw_key in raw_keys:
            hashed = self._hash_key(raw_key)
            key_id = f"bootstrap_{secrets.token_hex(4)}"
            entry = {
                "id": key_id,
                "label": "bootstrap",
                "prefix": raw_key[:12],
                "hashed_key": hashed,
                "created_at": datetime.now(UTC),
                "expires_at": None,
                "is_active": True,
                "last_used_at": None,
                "rate_limit_window": 0.0,
                "rate_limit_count": 0,
            }
            self._keys[key_id] = entry
        self._bootstrapped = True

    def create_key(self, label: str, expires_at: datetime | None = None) -> dict[str, Any]:
        raw_key = API_KEY_PREFIX + secrets.token_hex(32)
        key_id = secrets.token_hex(8)
        hashed = self._hash_key(raw_key)
        now = datetime.now(UTC)
        entry = {
            "id": key_id,
            "label": label,
            "prefix": raw_key[:12],
            "hashed_key": hashed,
            "created_at": now,
            "expires_at": expires_at,
            "is_active": True,
            "last_used_at": None,
            "rate_limit_window": 0.0,
            "rate_limit_count": 0,
        }
        self._keys[key_id] = entry
        if len(self._keys) > self._max_keys:
            self._keys.popitem(last=False)
        return {**entry, "key": raw_key}

    def get_key(self, key_id: str) -> dict[str, Any] | None:
        entry = self._keys.get(key_id)
        if entry is None:
            return None
        if not entry["is_active"]:
            return None
        if entry["expires_at"] and entry["expires_at"] < datetime.now(UTC):
            return None
        return entry

    def list_keys(self) -> list[dict[str, Any]]:
        now = datetime.now(UTC)
        return [
            {
                "id": e["id"],
                "label": e["label"],
                "prefix": e["prefix"],
                "created_at": e["created_at"],
                "expires_at": e["expires_at"],
                "is_active": e["is_active"] and (e["expires_at"] is None or e["expires_at"] > now),
                "last_used_at": e["last_used_at"],
            }
            for e in self._keys.values()
        ]

    def rotate_key(self, key_id: str) -> dict[str, Any] | None:
        entry = self._keys.get(key_id)
        if entry is None or not entry["is_active"]:
            return None
        raw_key = API_KEY_PREFIX + secrets.token_hex(32)
        entry["hashed_key"] = self._hash_key(raw_key)
        entry["prefix"] = raw_key[:12]
        return {**entry, "key": raw_key}

    def revoke_key(self, key_id: str) -> bool:
        entry = self._keys.get(key_id)
        if entry is None:
            return False
        entry["is_active"] = False
        return True

    def validate_key(self, raw_key: str) -> dict[str, Any] | None:
        for entry in self._keys.values():
            if not entry["is_active"]:
                continue
            if entry["expires_at"] and entry["expires_at"] < datetime.now(UTC):
                continue
            if hmac.compare_digest(self._hash_key(raw_key), entry["hashed_key"]):
                entry["last_used_at"] = time.time()
                return entry
        return None

    def check_rate_limit(self, key_id: str, max_requests: int, window_seconds: int) -> bool:
        entry = self._keys.get(key_id)
        if entry is None:
            return False
        now = time.time()
        if now - entry["rate_limit_window"] > window_seconds:
            entry["rate_limit_window"] = now
            entry["rate_limit_count"] = 1
            return True
        if entry["rate_limit_count"] >= max_requests:
            return False
        entry["rate_limit_count"] += 1
        return True

    @staticmethod
    def _hash_key(key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()


store = ApiKeyStore()