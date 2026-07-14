import logging
import re

from toon_format import decode as _toon_decode
from toon_format import encode as _toon_encode

logger = logging.getLogger("zam-ai-core-api.toon")

_TOON_BLOCK_RE = re.compile(r"```toon\s*\n?(.*?)\n?```", re.DOTALL)
_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*\n?(.*?)\n?```", re.DOTALL)
_CODE_BLOCK_RE = re.compile(r"```")


def encode_toon(data: object) -> str:
    try:
        return _toon_encode(data)
    except Exception:
        logger.exception("TOON encode failed, falling back to repr")
        return str(data)


def decode_toon(text: str) -> object | None:
    if not text or not text.strip():
        return None
    try:
        return _toon_decode(text.strip())
    except Exception:
        return None


def parse_response(text: str) -> dict | None:
    result = _try_parse_toon(text)
    if result is not None:
        return result
    result = _try_parse_json(text)
    if result is not None:
        return result
    return None


def _try_parse_toon(text: str) -> dict | None:
    match = _TOON_BLOCK_RE.search(text)
    if match:
        result = decode_toon(match.group(1).strip())
        if isinstance(result, dict):
            return result
    stripped = text.strip()
    if not stripped or stripped.startswith("{") or _CODE_BLOCK_RE.search(stripped):
        return None
    result = decode_toon(stripped)
    if isinstance(result, dict):
        return result
    return None


def _try_parse_json(text: str) -> dict | None:
    import json

    match = _JSON_BLOCK_RE.search(text)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return None
