export interface Citation {
  citation_id: string;
  text_content: string;
  score: number;
  source_name: string | null;
  source_version: string | null;
  source_trust_tier: number | null;
  document_title: string | null;
  section_path: string | null;
  page_number: number | null;
  chunk_type: string | null;
  generic_name: string | null;
  toDict(): Record<string, unknown>;
}

export interface CitationEngine {
  buildCitations(results: Record<string, unknown>[]): Citation[];
  buildEvidenceForPrompt(citations: Citation[]): Record<string, unknown>[];
  formatForResponse(citations: Citation[]): Record<string, unknown>[];
  deduplicate(citations: Citation[]): Citation[];
  truncate(citations: Citation[], max_count: number): Citation[];
  buildClaims(citations: Citation[], max_claims?: number): Record<string, unknown>[];
}
