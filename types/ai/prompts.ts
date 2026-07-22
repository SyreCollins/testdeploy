export interface PromptTemplate {
  path: string;
  name: string;
  version: string;
  owner: string;
  status: string;
  reviewed: string;
  supported_models: string[];
  content: string;
}

export interface PromptRegistry {
  loadAll(): void;
  get(key: string): PromptTemplate | undefined;
  listTemplates(): string[];
  reload(): void;
}

export interface PromptBuilder {
  add(templateKey: string, kwargs: Record<string, unknown>): void;
  addRaw(text: string): void;
  build(): string;
}

export interface PromptManager {
  buildMedicalQaPrompt(question: string, evidence: unknown[], patient_context: unknown): [string, string];
  buildInteractionCheckPrompt(medications: unknown[], evidence: unknown[], patient_context: unknown): [string, string];
  buildDrugInfoPrompt(drug_name: string, evidence: unknown[], requested_sections?: string[] | null): [string, string];
  buildSymptomGuidancePrompt(symptoms: string, patient_context: unknown): [string, string];
  buildContraindicationCheckPrompt(medications: unknown[], evidence: unknown[], patient_context: unknown): [string, string];
  buildDosageVerifyPrompt(medication: unknown, evidence: unknown[], patient_context: unknown): [string, string];
  buildPrescriptionExplainPrompt(prescription_text: string, evidence: unknown[], patient_context: unknown): [string, string];
  buildSystemPrompt(): string;
  getWorkflowVersion(workflow: string): string;
  listTemplates(): string[];
  reload(): void;
}
