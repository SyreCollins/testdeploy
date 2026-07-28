// ──────────────────────────────────────────────
// Shared nested types
// ──────────────────────────────────────────────

export interface ActorContext {
  actor_type: string;
  actor_id: string;
  organization_id: string | null;
  role: string;
}

export interface ConsentFlags {
  use_patient_context: boolean;
  store_ai_trace: boolean;
}

export interface AuthorizationContext {
  workflow: string;
  consent_flags: ConsentFlags;
  context_scope: string[];
}

export interface CallerInfo {
  service: string;
  environment: string;
}

export interface Locale {
  language: string;
  country: string;
}

export interface PatientContext {
  age: number | null;
  sex: string | null;
  known_conditions: string[];
  allergies: string[];
  current_medications: string[];
}

export interface ConversationContext {
  conversation_id: string | null;
  recent_messages: Record<string, unknown>[];
}

export interface SafetyMetadata {
  risk_level: string;
  action: string;
  requires_escalation: boolean;
  requires_human_review: boolean;
}

export interface ConfidenceMetadata {
  overall: number;
  grounding: number;
  retrieval: number;
}

export interface CitationItem {
  citation_id: string;
  text_content: string;
  score: number;
  source_name: string | null;
  source_version: string | null;
  source_trust_tier: number | null;
  document_title: string | null;
  section_path: string | null;
  page_number: number | null;
}

export interface AuditMetadata {
  trace_id: string | null;
  prompt_version: string | null;
  model_provider: string | null;
  model_version: string | null;
}

export interface ErrorDetail {
  code: string;
  message: string;
  retryable: boolean;
  details: Record<string, unknown> | null;
}

export interface ErrorResponse {
  request_id: string | null;
  status: "error";
  error: ErrorDetail;
  safety: SafetyMetadata | null;
}

// ──────────────────────────────────────────────
// Medical QA
// ──────────────────────────────────────────────

export interface MedicalQAInput {
  question: string;
  patient_context: PatientContext;
  conversation_context: ConversationContext;
}

export interface MedicalQARequest {
  request_id?: string | null;
  caller: CallerInfo;
  actor_context: ActorContext;
  authorization_context?: AuthorizationContext;
  locale?: Locale;
  input: MedicalQAInput;
}

export interface MedicalClaim {
  claim: string;
  citation_ids: string[];
}

export interface MedicalQAResult {
  answer: string;
  missing_context: string[];
  follow_up_questions: string[];
  medical_claims: MedicalClaim[];
}

export interface MedicalQAResponse {
  request_id: string | null;
  status: string;
  workflow: string;
  result: MedicalQAResult | null;
  safety: SafetyMetadata;
  citations: CitationItem[];
  confidence: ConfidenceMetadata;
  audit: AuditMetadata;
}

// ──────────────────────────────────────────────
// Symptom Guidance
// ──────────────────────────────────────────────

export interface SymptomGuidanceInput {
  symptoms: string;
  patient_context: PatientContext;
}

export interface SymptomGuidanceRequest {
  request_id?: string | null;
  caller: CallerInfo;
  actor_context: ActorContext;
  authorization_context?: AuthorizationContext;
  locale?: Locale;
  input: SymptomGuidanceInput;
}

export interface SymptomGuidanceResult {
  answer: string;
  triage_level: string;
  diagnosis_provided: boolean;
  follow_up_questions: string[];
}

export interface SymptomGuidanceResponse {
  request_id: string | null;
  status: string;
  workflow: string;
  result: SymptomGuidanceResult | null;
  safety: SafetyMetadata;
  citations: CitationItem[];
  confidence: ConfidenceMetadata;
  audit: AuditMetadata;
}

// ──────────────────────────────────────────────
// Interaction Check
// ──────────────────────────────────────────────

export interface InteractionMedication {
  name: string;
  dose: string | null;
}

export interface InteractionCheckInput {
  medications: InteractionMedication[];
  patient_context: PatientContext;
}

export interface InteractionCheckRequest {
  request_id?: string | null;
  caller: CallerInfo;
  actor_context: ActorContext;
  authorization_context?: AuthorizationContext;
  locale?: Locale;
  input: InteractionCheckInput;
}

export interface InteractionResult {
  medications: string[];
  severity: string;
  summary: string;
  recommended_action: string;
  citation_ids: string[];
}

export interface InteractionCheckResult {
  interactions: InteractionResult[];
  unknowns: string[];
  follow_up_questions: string[];
}

export interface InteractionCheckResponse {
  request_id: string | null;
  status: string;
  workflow: string;
  result: InteractionCheckResult | null;
  safety: SafetyMetadata;
  citations: CitationItem[];
  confidence: ConfidenceMetadata;
  audit: AuditMetadata;
}

// ──────────────────────────────────────────────
// Drug Info
// ──────────────────────────────────────────────

export interface DrugInfoInput {
  drug_name: string;
  requested_sections?: string[] | null;
  country?: string;
}

export interface DrugInfoRequest {
  request_id?: string | null;
  caller: CallerInfo;
  actor_context: ActorContext;
  authorization_context?: AuthorizationContext;
  locale?: Locale;
  input: DrugInfoInput;
}

export interface NormalizedDrug {
  input_name: string;
  generic_name: string | null;
  match_confidence: number;
}

export interface DrugInfoResult {
  normalized_drug: NormalizedDrug;
  sections: Record<string, string>;
  follow_up_questions: string[];
}

export interface DrugInfoResponse {
  request_id: string | null;
  status: string;
  workflow: string;
  result: DrugInfoResult | null;
  safety: SafetyMetadata;
  citations: CitationItem[];
  confidence: ConfidenceMetadata;
  audit: AuditMetadata;
}

// ──────────────────────────────────────────────
// Contraindication Check
// ──────────────────────────────────────────────

export interface ContraindicationMedication {
  name: string;
}

export interface ContraindicationCheckInput {
  medications: ContraindicationMedication[];
  patient_context: PatientContext;
}

export interface ContraindicationCheckRequest {
  request_id?: string | null;
  caller: CallerInfo;
  actor_context: ActorContext;
  authorization_context?: AuthorizationContext;
  locale?: Locale;
  input: ContraindicationCheckInput;
}

export interface ContraindicationItem {
  medication: string;
  condition: string;
  severity: string;
  reason: string;
  evidence_summary: string | null;
  citation_ids: string[];
}

export interface ContraindicationCheckResult {
  contraindications: ContraindicationItem[];
  missing_context: string[];
  unknowns: string[];
  follow_up_questions: string[];
}

export interface ContraindicationCheckResponse {
  request_id: string | null;
  status: string;
  workflow: string;
  result: ContraindicationCheckResult | null;
  safety: SafetyMetadata;
  citations: CitationItem[];
  confidence: ConfidenceMetadata;
  audit: AuditMetadata;
}

// ──────────────────────────────────────────────
// Dosage Verify
// ──────────────────────────────────────────────

export interface DosageMedication {
  name: string;
  strength: string | null;
  instructions: string | null;
}

export interface DosageVerifyInput {
  medication: DosageMedication;
  patient_context: PatientContext;
}

export interface DosageVerifyRequest {
  request_id?: string | null;
  caller: CallerInfo;
  actor_context: ActorContext;
  authorization_context?: AuthorizationContext;
  locale?: Locale;
  input: DosageVerifyInput;
}

export interface DosageResult {
  medication_name: string;
  stated_dosage: string;
  assessment: string;
  typical_range: string | null;
  flags: string[];
  citation_ids: string[];
}

export interface DosageVerifyResult {
  dosages: DosageResult[];
  missing_context: string[];
  follow_up_questions: string[];
}

export interface DosageVerifyResponse {
  request_id: string | null;
  status: string;
  workflow: string;
  result: DosageVerifyResult | null;
  safety: SafetyMetadata;
  citations: CitationItem[];
  confidence: ConfidenceMetadata;
  audit: AuditMetadata;
}

// ──────────────────────────────────────────────
// Prescription Explain
// ──────────────────────────────────────────────

export interface PrescriptionExplainInput {
  prescription_text: string;
  patient_context: PatientContext;
}

export interface PrescriptionExplainRequest {
  request_id?: string | null;
  caller: CallerInfo;
  actor_context: ActorContext;
  authorization_context?: AuthorizationContext;
  locale?: Locale;
  input: PrescriptionExplainInput;
}

export interface PrescriptionSection {
  title: string;
  content: string;
  citation_ids: string[];
}

export interface PrescriptionExplainResult {
  summary: string;
  sections: PrescriptionSection[];
  warnings: string[];
  follow_up_questions: string[];
}

export interface PrescriptionExplainResponse {
  request_id: string | null;
  status: string;
  workflow: string;
  result: PrescriptionExplainResult | null;
  safety: SafetyMetadata;
  citations: CitationItem[];
  confidence: ConfidenceMetadata;
  audit: AuditMetadata;
}

// ──────────────────────────────────────────────
// Chat
// ──────────────────────────────────────────────

export interface ChatInput {
  message: string;
  patient_context: PatientContext;
  conversation_context: ConversationContext;
}

export interface ChatRequest {
  request_id?: string | null;
  caller: CallerInfo;
  actor_context: ActorContext;
  authorization_context?: AuthorizationContext;
  locale?: Locale;
  input: ChatInput;
}

export interface ChatResult {
  intent: string;
  confidence: number;
  answer: string;
}

export interface ChatResponse {
  request_id: string | null;
  status: string;
  workflow: string;
  result: ChatResult | null;
  safety: SafetyMetadata;
  citations: CitationItem[];
  confidence: ConfidenceMetadata;
  audit: AuditMetadata;
}

// ──────────────────────────────────────────────
// Prescriptions OCR
// ──────────────────────────────────────────────

export interface PrescriptionOcrCreateInput {
  image_data: string;
  image_format: string;
}

export interface PrescriptionOcrCreateRequest {
  request_id?: string | null;
  caller: CallerInfo;
  actor_context: ActorContext;
  authorization_context?: AuthorizationContext;
  locale?: Locale;
  input: PrescriptionOcrCreateInput;
}

export interface PrescriptionOcrJob {
  job_id: string;
  status: string;
  created_at: string;
  completed_at: string | null;
  extracted_text: string | null;
  error: string | null;
}

export interface PrescriptionOcrCreateResult {
  job: PrescriptionOcrJob;
}

export interface PrescriptionOcrCreateResponse {
  request_id: string | null;
  status: string;
  workflow: string;
  result: PrescriptionOcrCreateResult | null;
  safety: SafetyMetadata;
  citations: CitationItem[];
  confidence: ConfidenceMetadata;
  audit: AuditMetadata;
}

export interface PrescriptionOcrPollResponse {
  request_id: string | null;
  status: string;
  workflow: string;
  result: PrescriptionOcrJob | null;
  safety: SafetyMetadata;
  citations: CitationItem[];
  confidence: ConfidenceMetadata;
  audit: AuditMetadata;
}

// ──────────────────────────────────────────────
// Reminders Parse Schedule
// ──────────────────────────────────────────────

export interface ReminderParseInput {
  raw_text: string;
}

export interface ReminderParseRequest {
  request_id?: string | null;
  caller: CallerInfo;
  actor_context: ActorContext;
  authorization_context?: AuthorizationContext;
  locale?: Locale;
  input: ReminderParseInput;
}

export interface ParsedReminder {
  medication_name: string;
  dosage: string | null;
  frequency: string;
  time_of_day: string[];
  start_date: string | null;
  notes: string | null;
}

export interface ReminderParseResult {
  reminders: ParsedReminder[];
  unparsed_text: string | null;
}

export interface ReminderParseResponse {
  request_id: string | null;
  status: string;
  workflow: string;
  result: ReminderParseResult | null;
  safety: SafetyMetadata;
  citations: CitationItem[];
  confidence: ConfidenceMetadata;
  audit: AuditMetadata;
}

// ──────────────────────────────────────────────
// Doctor Assist
// ──────────────────────────────────────────────

export interface DoctorAssistInput {
  query: string;
  patient_context: PatientContext;
  conversation_context: ConversationContext;
}

export interface DoctorAssistRequest {
  request_id?: string | null;
  caller: CallerInfo;
  actor_context: ActorContext;
  authorization_context?: AuthorizationContext;
  locale?: Locale;
  input: DoctorAssistInput;
}

export interface DoctorAssistResult {
  answer: string;
  recommendations: string[];
  differential_diagnoses: string[] | null;
  follow_up_questions: string[];
}

export interface DoctorAssistResponse {
  request_id: string | null;
  status: string;
  workflow: string;
  result: DoctorAssistResult | null;
  safety: SafetyMetadata;
  citations: CitationItem[];
  confidence: ConfidenceMetadata;
  audit: AuditMetadata;
}

// ──────────────────────────────────────────────
// Pharmacy Assist
// ──────────────────────────────────────────────

export interface PharmacyAssistInput {
  query: string;
  patient_context: PatientContext;
  conversation_context: ConversationContext;
}

export interface PharmacyAssistRequest {
  request_id?: string | null;
  caller: CallerInfo;
  actor_context: ActorContext;
  authorization_context?: AuthorizationContext;
  locale?: Locale;
  input: PharmacyAssistInput;
}

export interface PharmacyAssistResult {
  answer: string;
  alternative_medications: string[] | null;
  insurance_notes: string[] | null;
  follow_up_questions: string[];
}

export interface PharmacyAssistResponse {
  request_id: string | null;
  status: string;
  workflow: string;
  result: PharmacyAssistResult | null;
  safety: SafetyMetadata;
  citations: CitationItem[];
  confidence: ConfidenceMetadata;
  audit: AuditMetadata;
}
