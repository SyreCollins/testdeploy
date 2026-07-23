import hashlib
import hmac
import secrets
import time
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlmodel import Session as SASession

from app.db.engine import get_session
from app.db.models.platform import ApiKey

API_KEY_PREFIX = "zam_"


class ApiKeyStore:
    _engine = None

    def bootstrap_static_keys(self, raw_keys: list[str]) -> None:
        with get_session(self._engine) as session:
            existing = session.exec(select(ApiKey).where(ApiKey.label == "bootstrap")).first()
            if existing:
                return
            for raw_key in raw_keys:
                hashed = self._hash_key(raw_key)
                entry = ApiKey(
                    id=f"bootstrap_{secrets.token_hex(4)}",
                    label="bootstrap",
                    prefix=raw_key[:12],
                    hashed_key=hashed,
                    is_active=True,
                    rate_limit_window=0.0,
                    rate_limit_count=0,
                )
                session.add(entry)
            session.commit()

    def create_key(
        self, label: str, expires_at: datetime | None = None,
        project_id: int | None = None,
    ) -> dict[str, Any]:
        raw_key = API_KEY_PREFIX + secrets.token_hex(32)
        key_id = secrets.token_hex(8)
        hashed = self._hash_key(raw_key)
        now = datetime.now(UTC)
        entry = ApiKey(
            id=key_id,
            label=label,
            prefix=raw_key[:12],
            hashed_key=hashed,
            created_at=now,
            expires_at=expires_at,
            is_active=True,
            rate_limit_window=0.0,
            rate_limit_count=0,
            project_id=project_id,
        )
        with get_session(self._engine) as session:
            session.add(entry)
            session.commit()
            session.refresh(entry)
        return {
            "id": entry.id,
            "label": entry.label,
            "prefix": entry.prefix,
            "created_at": entry.created_at,
            "expires_at": entry.expires_at,
            "is_active": entry.is_active,
            "key": raw_key,
            "project_id": entry.project_id,
        }

    def get_key(self, key_id: str) -> dict[str, Any] | None:
        with get_session(self._engine) as session:
            entry = session.get(ApiKey, key_id)
            if entry is None:
                return None
            if not entry.is_active:
                return None
            if entry.expires_at and entry.expires_at < datetime.now(UTC):
                return None
            return {
                "id": entry.id,
                "label": entry.label,
                "prefix": entry.prefix,
                "hashed_key": entry.hashed_key,
                "created_at": entry.created_at,
                "expires_at": entry.expires_at,
                "is_active": entry.is_active,
                "last_used_at": entry.last_used_at,
                "rate_limit_window": entry.rate_limit_window,
                "rate_limit_count": entry.rate_limit_count,
                "project_id": entry.project_id,
            }

    def list_keys(self) -> list[dict[str, Any]]:
        now = datetime.now(UTC)
        with get_session(self._engine) as session:
            entries = session.exec(select(ApiKey)).all()
            return [
                {
                    "id": e.id,
                    "label": e.label,
                    "prefix": e.prefix,
                    "created_at": e.created_at,
                    "expires_at": e.expires_at,
                    "is_active": e.is_active and (e.expires_at is None or e.expires_at > now),
                    "last_used_at": e.last_used_at,
                    "project_id": e.project_id,
                }
                for e in entries
            ]

    def rotate_key(self, key_id: str) -> dict[str, Any] | None:
        with get_session(self._engine) as session:
            entry = session.get(ApiKey, key_id)
            if entry is None or not entry.is_active:
                return None
            raw_key = API_KEY_PREFIX + secrets.token_hex(32)
            entry.hashed_key = self._hash_key(raw_key)
            entry.prefix = raw_key[:12]
            session.add(entry)
            session.commit()
            session.refresh(entry)
            return {
                "id": entry.id,
                "label": entry.label,
                "prefix": entry.prefix,
                "created_at": entry.created_at,
                "expires_at": entry.expires_at,
                "is_active": entry.is_active,
                "key": raw_key,
                "project_id": entry.project_id,
            }

    def revoke_key(self, key_id: str) -> bool:
        with get_session(self._engine) as session:
            entry = session.get(ApiKey, key_id)
            if entry is None:
                return False
            entry.is_active = False
            session.add(entry)
            session.commit()
            return True

    def validate_key(self, raw_key: str) -> dict[str, Any] | None:
        provided_hash = self._hash_key(raw_key)
        with get_session(self._engine) as session:
            entries = session.exec(
                select(ApiKey).where(ApiKey.is_active.is_(True))
            ).all()
            for entry in entries:
                if entry.expires_at and entry.expires_at < datetime.now(UTC):
                    continue
                if hmac.compare_digest(provided_hash, entry.hashed_key):
                    entry.last_used_at = time.time()
                    session.add(entry)
                    session.commit()
                    return {
                        "id": entry.id,
                        "label": entry.label,
                        "hashed_key": entry.hashed_key,
                        "rate_limit_window": entry.rate_limit_window,
                        "rate_limit_count": entry.rate_limit_count,
                        "project_id": entry.project_id,
                        "is_active": entry.is_active,
                        "expires_at": entry.expires_at,
                    }
            return None

    def check_rate_limit(self, key_id: str, max_requests: int, window_seconds: int) -> bool:
        with get_session(self._engine) as session:
            entry = session.get(ApiKey, key_id)
            if entry is None:
                return False
            now = time.time()
            if now - entry.rate_limit_window > window_seconds:
                entry.rate_limit_window = now
                entry.rate_limit_count = 1
                session.add(entry)
                session.commit()
                return True
            if entry.rate_limit_count >= max_requests:
                return False
            entry.rate_limit_count += 1
            session.add(entry)
            session.commit()
            return True

    @staticmethod
    def _hash_key(key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()


store = ApiKeyStore()