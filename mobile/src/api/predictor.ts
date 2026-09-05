import { request } from "./client";

export interface PredictorOption {
  id: number;
  name: string;
}

interface OptionsResponse {
  exams: PredictorOption[];
  categories: PredictorOption[];
  quotas: PredictorOption[];
}

export function getOptions(): Promise<OptionsResponse> {
  return request("/predictor/options");
}

// Mirrors search_colleges()'s raw result dict exactly (services/prediction_
// service.py) -- note the "college" key, not "college_name", and the
// presence of round/year. This is a different shape from the AI block's
// PredictionCardData (response_blocks/builders.py's _college_card_data()
// explicitly renames college -> college_name and drops round/year when
// building that one) -- not the same data wearing two hats.
export interface PredictorResult {
  college_id: number;
  college: string;
  branch: string;
  exam: string;
  category: string;
  quota: string;
  round: number;
  year: number;
  closing_rank: number;
  avg_package: number | null;
  median_package: number | null;
  placement_rate: number | null;
  nirf_rank: number | null;
  fees: number | null;
  hostel_fees: number | null;
  website: string | null;
}

interface PredictResponse {
  prediction_id: number;
  results: PredictorResult[];
}

export function predict(
  exam: string,
  category: string,
  quota: string,
  rank: number
): Promise<PredictResponse> {
  return request("/predictor/predict", {
    method: "POST",
    body: JSON.stringify({ exam, category, quota, rank }),
  });
}
