import hashlib
import hmac
import secrets
import time
from datetime import UTC, datetime
from typing import Any

from sqlmodel import Session

from app.core.config import PLAN_FREE
from app.db.models.platform import ApiKey, Organization, Project

API_KEY_PREFIX = "zam_"


class ApiKeyStore:
    _engine = None
    _rate_cache: dict[str, dict[str, float | int]] = {}

    def bootstrap_static_keys(self, raw_keys: list[str]) -> None:
        with Session(self._engine) as session:
            existing = session.query(ApiKey).filter(ApiKey.label == "bootstrap").first()
            if existing:
                return
            for raw_key in raw_keys:
                hashed = self._hash_key(raw_key)
                entry = ApiKey(
                    id=f"bootstrap_{secrets.token_hex(4)}",
                    label="bootstrap",
                    prefix=raw_key[:12],
                    key_hash=hashed,
                    is_active=True,
                )
                session.add(entry)
            session.commit()

    def create_key(
        self, label: str, expires_at: datetime | None = None,
        organization_id: int | None = None, project_id: int | None = None,
    ) -> dict[str, Any]:
        raw_key = API_KEY_PREFIX + secrets.token_hex(32)
        key_id = secrets.token_hex(8)
        hashed = self._hash_key(raw_key)
        now = datetime.now(UTC)
        entry = ApiKey(
            id=key_id,
            label=label,
            prefix=raw_key[:12],
            key_hash=hashed,
            created_at=now,
            expires_at=expires_at,
            is_active=True,
            organization_id=organization_id,
            project_id=project_id,
        )
        with Session(self._engine) as session:
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
        with Session(self._engine) as session:
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
                "key_hash": entry.key_hash,
                "created_at": entry.created_at,
                "expires_at": entry.expires_at,
                "is_active": entry.is_active,
                "last_used_at": entry.last_used_at,
                "organization_id": entry.organization_id,
                "project_id": entry.project_id,
            }

    def list_keys(self, organization_id: int | None = None) -> list[dict[str, Any]]:
        now = datetime.now(UTC)
        with Session(self._engine) as session:
            query = session.query(ApiKey)
            if organization_id is not None:
                query = query.filter(ApiKey.organization_id == organization_id)
            entries = query.all()
            return [
                {
                    "id": e.id,
                    "label": e.label,
                    "prefix": e.prefix,
                    "created_at": e.created_at,
                    "expires_at": e.expires_at,
                    "is_active": e.is_active and (e.expires_at is None or e.expires_at > now),
                    "last_used_at": e.last_used_at,
                    "organization_id": e.organization_id,
                    "project_id": e.project_id,
                }
                for e in entries
            ]

    def rotate_key(self, key_id: str) -> dict[str, Any] | None:
        with Session(self._engine) as session:
            entry = session.get(ApiKey, key_id)
            if entry is None or not entry.is_active:
                return None
            raw_key = API_KEY_PREFIX + secrets.token_hex(32)
            entry.key_hash = self._hash_key(raw_key)
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
        with Session(self._engine) as session:
            entry = session.get(ApiKey, key_id)
            if entry is None:
                return False
            entry.is_active = False
            session.add(entry)
            session.commit()
            return True

    def validate_key(self, raw_key: str) -> dict[str, Any] | None:
        provided_hash = self._hash_key(raw_key)
        with Session(self._engine) as session:
            entries = session.query(ApiKey).filter(ApiKey.is_active.is_(True)).all()
            for entry in entries:
                if entry.expires_at and entry.expires_at < datetime.now(UTC):
                    continue
                if hmac.compare_digest(provided_hash, entry.key_hash):
                    entry.last_used_at = datetime.now(UTC)
                    session.add(entry)
                    session.commit()
                    org_plan = PLAN_FREE
                    org_id = entry.organization_id
                    if entry.project_id is not None:
                        project = session.get(Project, entry.project_id)
                        if project is not None:
                            org_id = project.organization_id
                    if org_id is not None:
                        org = session.get(Organization, org_id)
                        if org is not None:
                            org_plan = org.plan
                    return {
                        "id": entry.id,
                        "label": entry.label,
                        "key_hash": entry.key_hash,
                        "project_id": entry.project_id,
                        "org_plan": org_plan,
                        "org_id": entry.organization_id,
                        "is_active": entry.is_active,
                        "expires_at": entry.expires_at,
                    }
            return None

    def check_rate_limit(self, key_id: str, max_requests: int, window_seconds: int) -> bool:
        now = time.time()
        cached = self._rate_cache.get(key_id)
        if cached is None or now - cached["window"] > window_seconds:
            self._rate_cache[key_id] = {"window": now, "count": 1}
            return True
        if cached["count"] >= max_requests:
            return False
        cached["count"] += 1
        return True

    @staticmethod
    def _hash_key(key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()


store = ApiKeyStore()