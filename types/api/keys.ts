export interface CreateApiKeyRequest {
  label: string;
  expires_at?: string | null;
}

export interface CreateApiKeyResponse {
  id: string;
  label: string;
  key: string;
  prefix: string;
  created_at: string;
  expires_at: string | null;
  is_active: boolean;
}

export interface ApiKeyInfo {
  id: string;
  label: string;
  prefix: string;
  created_at: string;
  expires_at: string | null;
  is_active: boolean;
  last_used_at: string | null;
}

export interface ListApiKeysResponse {
  keys: ApiKeyInfo[];
}

export interface RotateApiKeyResponse {
  id: string;
  new_key: string;
}

export interface RevokeApiKeyResponse {
  id: string;
  revoked: boolean;
}
