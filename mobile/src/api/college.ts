import { request } from "./client";

// Mirrors serialize_college() exactly -- this is also the shape of the
// nested `college` object on a comparison branch (api/comparison.ts),
// since both come from the same serializer. serialize_college() itself
// never includes branches; only GET /colleges/<id>'s handler attaches
// that separately, hence CollegeDetail extending this rather than baking
// branches in here.
export interface College {
  id: number;
  name: string;
  location: string | null;
  state: string | null;
  college_type: string | null;
  fees: number | null;
  hostel_fees: number | null;
  nirf_rank: number | null;
  website: string | null;
}

// Mirrors serialize_branch(branch, include_college=False) exactly -- the
// college.branches items never carry a nested college back-reference.
export interface CollegeBranch {
  id: number;
  branch_name: string;
  branch_code: string | null;
  intake: number | null;
  avg_package: number | null;
  median_package: number | null;
  placement_rate: number | null;
}

// Mirrors GET /colleges/<id>'s shape exactly -- this is the only endpoint
// that attaches `branches`; serialize_college() elsewhere (saved colleges,
// prediction/recommendation block data, comparison branches) never
// includes it.
export interface CollegeDetail extends College {
  branches: CollegeBranch[];
}

export function getCollege(id: number): Promise<{ college: CollegeDetail }> {
  return request(`/colleges/${id}`);
}
