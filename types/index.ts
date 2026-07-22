// ──────────────────────────────────────────────
// Core
// ──────────────────────────────────────────────
export type { Settings } from "./core/config";
export type { ErrorDetail, ApiErrorResponse, SafetyMetadata } from "./core/errors";

// ──────────────────────────────────────────────
// RAG
// ──────────────────────────────────────────────
export type {
  MedicalSource,
  SourceDocument,
  DocumentChunk,
  Citation as RagCitation,
} from "./rag/schemas";

// ──────────────────────────────────────────────
// AI - Gateway
// ──────────────────────────────────────────────
export type { ModelResponse, StreamEvent, BaseModelProvider } from "./ai/gateway";

// ──────────────────────────────────────────────
// AI - Orchestrator
// ──────────────────────────────────────────────
export { Intent } from "./ai/orchestrator";
export type { Message, ConversationState, WorkflowResult } from "./ai/orchestrator";

// ──────────────────────────────────────────────
// AI - Audit
// ──────────────────────────────────────────────
export type { AuditEvent, AuditTrace, AuditTraceWriter } from "./ai/audit";

// ──────────────────────────────────────────────
// AI - Citation
// ──────────────────────────────────────────────
export type { Citation, CitationEngine } from "./ai/citation";

// ──────────────────────────────────────────────
// AI - Grounding
// ──────────────────────────────────────────────
export type { GroundingDetail, GroundingResult } from "./ai/grounding";

// ──────────────────────────────────────────────
// AI - Safety
// ──────────────────────────────────────────────
export { RiskLevel, SafetyAction } from "./ai/safety";
export type { SafetyDecision, SafetyContext } from "./ai/safety";

// ──────────────────────────────────────────────
// AI - Prompts
// ──────────────────────────────────────────────
export type {
  PromptTemplate,
  PromptRegistry,
  PromptBuilder,
  PromptManager,
} from "./ai/prompts";

// ──────────────────────────────────────────────
// AI - Scoring
// ──────────────────────────────────────────────
export type { ConfidenceScorer, ConfidenceMetadata } from "./ai/scoring";

// ──────────────────────────────────────────────
// API - Health
// ──────────────────────────────────────────────
export type { HealthResponse, DependencyStatus, ReadinessResponse } from "./api/health";

// ──────────────────────────────────────────────
// API - Retrieval
// ──────────────────────────────────────────────
export type { SearchRequest, SearchResultItem, SearchResponse } from "./api/retrieval";

// ──────────────────────────────────────────────
// API - Audit
// ──────────────────────────────────────────────
export type {
  AuditEventSummary,
  AuditTraceInfo,
  ListAuditTracesResponse,
  GetAuditTraceResponse,
} from "./api/audit";

// ──────────────────────────────────────────────
// API - Keys
// ──────────────────────────────────────────────
export type {
  CreateApiKeyRequest,
  CreateApiKeyResponse,
  ApiKeyInfo,
  ListApiKeysResponse,
  RotateApiKeyResponse,
  RevokeApiKeyResponse,
} from "./api/keys";

// ──────────────────────────────────────────────
// API - AI (all request/response types)
// ──────────────────────────────────────────────
export type {
  ActorContext,
  ConsentFlags,
  AuthorizationContext,
  CallerInfo,
  Locale,
  PatientContext,
  ConversationContext,
  SafetyMetadata as ApiSafetyMetadata,
  ConfidenceMetadata as ApiConfidenceMetadata,
  CitationItem,
  AuditMetadata,
  ErrorDetail as ApiErrorDetail,
  ErrorResponse,
  MedicalQAInput,
  MedicalQARequest,
  MedicalClaim,
  MedicalQAResult,
  MedicalQAResponse,
  SymptomGuidanceInput,
  SymptomGuidanceRequest,
  SymptomGuidanceResult,
  SymptomGuidanceResponse,
  InteractionMedication,
  InteractionCheckInput,
  InteractionCheckRequest,
  InteractionResult,
  InteractionCheckResult,
  InteractionCheckResponse,
  DrugInfoInput,
  DrugInfoRequest,
  NormalizedDrug,
  DrugInfoResult,
  DrugInfoResponse,
  ContraindicationMedication,
  ContraindicationCheckInput,
  ContraindicationCheckRequest,
  ContraindicationItem,
  ContraindicationCheckResult,
  ContraindicationCheckResponse,
  DosageMedication,
  DosageVerifyInput,
  DosageVerifyRequest,
  DosageResult,
  DosageVerifyResult,
  DosageVerifyResponse,
  PrescriptionExplainInput,
  PrescriptionExplainRequest,
  PrescriptionSection,
  PrescriptionExplainResult,
  PrescriptionExplainResponse,
  ChatInput,
  ChatRequest,
  ChatResult,
  ChatResponse,
} from "./api/ai";
