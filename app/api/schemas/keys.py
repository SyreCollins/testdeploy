from datetime import datetime

from pydantic import BaseModel, Field


class CreateApiKeyRequest(BaseModel):
    label: str = Field(min_length=1, max_length=100, description="Human-readable label for the key")
    expires_at: datetime | None = None
    organization_id: int = Field(description="Organization to scope this key to")


class CreateApiKeyResponse(BaseModel):
    id: str
    label: str
    key: str
    prefix: str
    created_at: datetime
    expires_at: datetime | None = None
    is_active: bool


class ApiKeyInfo(BaseModel):
    id: str
    label: str
    prefix: str
    created_at: datetime
    expires_at: datetime | None = None
    is_active: bool
    last_used_at: datetime | None = None


class ListApiKeysResponse(BaseModel):
    keys: list[ApiKeyInfo]


class RotateApiKeyResponse(BaseModel):
    id: str
    new_key: str


class RevokeApiKeyResponse(BaseModel):
    id: str
    revoked: bool