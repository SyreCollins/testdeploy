export interface MedicalSource {
  id: number | null;
  name: string;
  publisher: string;
  version: string;
  license_status: string;
  jurisdiction: string;
  trust_tier: number | null;
  publication_date: string | null;
  ingested_at: string;
}

export interface SourceDocument {
  id: number | null;
  source_id: number;
  title: string;
  file_path: string;
  checksum: string;
  document_version: string | null;
  parsed_at: string | null;
  status: "pending" | "parsed" | "failed";
}

export interface DocumentChunk {
  id: string;
  document_id: number;
  chunk_type: string;
  section_path: string;
  page_number: number | null;
  text_content: string;
  embedding_id: string | null;
  generic_name: string | null;
  brand_names: string | null;
  drug_entity_id: string | null;
  source_trust_tier: number | null;
}

export interface Citation {
  citation_id: string;
  source_name: string;
  source_version: string;
  source_trust_tier: number | null;
  document_title: string;
  section_path: string;
  page_number: number | null;
  text_content: string;
}
