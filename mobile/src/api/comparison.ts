import { College } from "./college";
import { request } from "./client";

// Mirrors serialize_branch(branch) exactly -- both GET /branches and
// POST /compare use the default include_college=True, so the nested
// `college` object here is the same College shape as api/college.ts's
// CollegeDetail (minus branches). This is a different shape from the AI
// chat's ComparisonBranchData (features/ai-counselor/components/blocks/
// types.ts) -- that one comes from a different serializer
// (_branch_data() in services/comparison_service.py), flat with `college`
// as a plain string, not the same data wearing two hats.
export interface ComparisonBranch {
  id: number;
  branch_name: string;
  branch_code: string | null;
  intake: number | null;
  avg_package: number | null;
  median_package: number | null;
  placement_rate: number | null;
  college: College;
}

// GET /comparison/branches has no query-param filtering (confirmed by
// reading the route -- it's an unconditional Branch.query.all()), so
// callers fetch once and filter client-side rather than debouncing a
// server round-trip that doesn't exist.
export function getBranches(): Promise<{ branches: ComparisonBranch[] }> {
  return request("/comparison/branches");
}

interface CompareResponse {
  comparison_id: number;
  branch1: ComparisonBranch;
  branch2: ComparisonBranch;
}

export function compare(branch1Id: number, branch2Id: number): Promise<CompareResponse> {
  return request("/comparison/compare", {
    method: "POST",
    body: JSON.stringify({ branch1_id: branch1Id, branch2_id: branch2Id }),
  });
}
