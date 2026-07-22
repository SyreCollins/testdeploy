export interface SearchRequest {
  query: string;
  limit?: number;
  generic_name_filter?: string | null;
  chunk_type_filter?: string | null;
  min_trust_tier?: number | null;
}

export interface SearchResultItem {
  citation_id: string;
  text_content: string;
  score: number;
  section_path: string | null;
  page_number: number | null;
  generic_name: string | null;
  chunk_type: string | null;
  source_name: string | null;
  source_version: string | null;
  source_trust_tier: number | null;
  document_title: string | null;
}

export interface SearchResponse {
  query: string;
  results: SearchResultItem[];
  total: number;
}
