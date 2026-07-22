export interface GroundingDetail {
  claim: string;
  is_grounded: boolean;
  overlap_score: number;
  supporting_evidence: string[];
}

export interface GroundingResult {
  score: number;
  grounded_claims: number;
  total_claims: number;
  details: GroundingDetail[];
}
