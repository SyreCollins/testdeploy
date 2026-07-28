// ──────────────────────────────────────────────
// Project
// ──────────────────────────────────────────────

export interface ProjectInfo {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

// ──────────────────────────────────────────────
// List & Create
// ──────────────────────────────────────────────

export interface CreateProjectRequest {
  name: string;
  description?: string | null;
}

export interface ListProjectsResponse {
  projects: ProjectInfo[];
}

export interface CreateProjectResponse {
  project: ProjectInfo;
}

// ──────────────────────────────────────────────
// Detail, Update, Delete
// ──────────────────────────────────────────────

export interface UpdateProjectRequest {
  name?: string;
  description?: string | null;
}

export interface ProjectDetailResponse {
  project: ProjectInfo;
}

export interface DeleteProjectResponse {
  deleted: boolean;
}

// ──────────────────────────────────────────────
// Project API Keys
// ──────────────────────────────────────────────

export interface CreateProjectApiKeyRequest {
  label: string;
  expires_at?: string | null;
}

export interface ProjectApiKeyInfo {
  id: string;
  label: string;
  prefix: string;
  created_at: string;
  expires_at: string | null;
  is_active: boolean;
  last_used_at: string | null;
}

export interface ListProjectApiKeysResponse {
  keys: ProjectApiKeyInfo[];
}

export interface CreateProjectApiKeyResponse {
  id: string;
  label: string;
  key: string;
  prefix: string;
  created_at: string;
  expires_at: string | null;
  is_active: boolean;
}

export interface RotateProjectApiKeyResponse {
  id: string;
  new_key: string;
}

export interface RevokeProjectApiKeyResponse {
  id: string;
  revoked: boolean;
}