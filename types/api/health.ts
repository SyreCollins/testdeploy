export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  environment: string;
}

export interface DependencyStatus {
  status: string;
  detail: string | null;
}

export interface ReadinessResponse {
  status: string;
  dependencies: Record<string, DependencyStatus>;
}
