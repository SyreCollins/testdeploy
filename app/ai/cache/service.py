import hashlib
import json
import logging
import time
from copy import deepcopy
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.ai.orchestrator.models import WorkflowResult

logger = logging.getLogger("zam-ai-core-api.cache")


class ResponseCache:
    def __init__(self, default_ttl: int = 3600, max_size: int = 1000) -> None:
        self._default_ttl = default_ttl
        self._max_size = max_size
        self._cache: dict[str, tuple[float, WorkflowResult]] = {}

    def make_key(self, workflow: str, **kwargs: Any) -> str:
        serializable = {}
        for k, v in kwargs.items():
            if isinstance(v, list):
                serializable[k] = sorted(
                    json.dumps(item, sort_keys=True, default=str) if isinstance(item, dict) else str(item)
                    for item in v
                )
            elif isinstance(v, dict):
                serializable[k] = json.dumps(v, sort_keys=True, default=str)
            elif isinstance(v, str):
                serializable[k] = v
            elif v is not None:
                serializable[k] = str(v)
        content = json.dumps({"workflow": workflow, **serializable}, sort_keys=True)
        h = hashlib.sha256(content.encode()).hexdigest()
        return f"{workflow}_{h}"

    def get(self, key: str) -> "WorkflowResult | None":

        entry = self._cache.get(key)
        if entry is None:
            return None
        expiry, result = entry
        if time.time() > expiry:
            del self._cache[key]
            return None
        return deepcopy(result)

    def set(self, key: str, result: "WorkflowResult", ttl: int | None = None) -> None:
        if len(self._cache) >= self._max_size:
            self._evict_one()
        self._cache[key] = (time.time() + (ttl or self._default_ttl), deepcopy(result))

    def invalidate(self, workflow: str | None = None) -> int:
        if workflow is None:
            count = len(self._cache)
            self._cache.clear()
            logger.info("Cache invalidated (all)")
            return count
        keys_to_remove = [k for k in self._cache if k.startswith(f"{workflow}_")]
        for k in keys_to_remove:
            del self._cache[k]
        if keys_to_remove:
            logger.info("Cache invalidated for workflow '%s': %d entries", workflow, len(keys_to_remove))
        return len(keys_to_remove)

    def _evict_one(self) -> None:
        try:
            oldest_key = min(self._cache, key=lambda k: self._cache[k][0])
            del self._cache[oldest_key]
        except ValueError:
            pass

    @property
    def size(self) -> int:
        return len(self._cache)
