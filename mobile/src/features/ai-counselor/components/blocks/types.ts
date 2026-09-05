// Mirrors response_blocks/builders.py's _college_card_data() exactly.
export interface RecommendationCardData {
  college_id: number | null;
  college_name: string | null;
  branch: string | null;
  closing_rank: number | null;
  avg_package: number | null;
  median_package: number | null;
  placement_rate: number | null;
  nirf_rank: number | null;
  fees: number | null;
  hostel_fees: number | null;
  website: string | null;
}

// build_prediction_blocks() adds exam/category/quota on top of the same
// base fields as recommendation_card.
export interface PredictionCardData extends RecommendationCardData {
  exam: string | null;
  category: string | null;
  quota: string | null;
}

export interface ComparisonBranchData {
  college: string | null;
  branch: string | null;
  avg_package: number | null;
  median_package: number | null;
  placement_rate: number | null;
  fees: number | null;
  nirf_rank: number | null;
  // college_id was additive-but-unread until Phase 6 gave ComparisonCard a
  // real "View Details" action to wire up; declared now since it's
  // actually read. branch_id/branch_code/intake/location/state/
  // college_type still exist on the wire but remain unread here.
  college_id: number | null;
  hostel_fees?: number | null;
  website?: string | null;
}

export interface ComparisonCardData {
  branch_1: ComparisonBranchData;
  branch_2: ComparisonBranchData;
}
