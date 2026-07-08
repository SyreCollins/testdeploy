import logging

from fastapi import APIRouter, HTTPException
from starlette import status

from app.api.keys.service import store
from app.api.schemas.keys import (
    ApiKeyInfo,
    CreateApiKeyRequest,
    CreateApiKeyResponse,
    ListApiKeysResponse,
    RevokeApiKeyResponse,
    RotateApiKeyResponse,
)

logger = logging.getLogger("zam-ai-core-api.key-routes")
router = APIRouter()


@router.post(
    "/keys",
    response_model=CreateApiKeyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_key(body: CreateApiKeyRequest) -> CreateApiKeyResponse:
    result = store.create_key(label=body.label, expires_at=body.expires_at)
    return CreateApiKeyResponse(
        id=result["id"],
        label=result["label"],
        key=result["key"],
        prefix=result["prefix"],
        created_at=result["created_at"],
        expires_at=result["expires_at"],
        is_active=result["is_active"],
    )


@router.get(
    "/keys",
    response_model=ListApiKeysResponse,
)
def list_keys() -> ListApiKeysResponse:
    keys = store.list_keys()
    return ListApiKeysResponse(
        keys=[ApiKeyInfo(**k) for k in keys]
    )


@router.post(
    "/keys/{key_id}/rotate",
    response_model=RotateApiKeyResponse,
)
def rotate_key(key_id: str) -> RotateApiKeyResponse:
    result = store.rotate_key(key_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Key not found or inactive")
    return RotateApiKeyResponse(id=result["id"], new_key=result["key"])


@router.post(
    "/keys/{key_id}/revoke",
    response_model=RevokeApiKeyResponse,
)
def revoke_key(key_id: str) -> RevokeApiKeyResponse:
    revoked = store.revoke_key(key_id)
    if not revoked:
        raise HTTPException(status_code=404, detail="Key not found")
    return RevokeApiKeyResponse(id=key_id, revoked=True)