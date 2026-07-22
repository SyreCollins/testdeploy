export interface ConfidenceScorer {
  scoreRetrieval(citations: Citation[]): number;
  scoreGrounding(response_text: string, citations: Citation[]): number;
  scoreOverall(retrieval: number, grounding: number): number;
  compute(citations: Citation[], response_text: string): Record<string, number>;
}

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
}

export interface ConfidenceMetadata {
  overall: number;
  grounding: number;
  retrieval: number;
}
