// PredictorResult/ComparisonBranch themselves are defined in their
// respective api/*.ts files, since they're wire-shape concerns, not
// navigation ones -- imported here so this file stays the single source
// of truth for every param list.
import { PredictorResult } from "../api/predictor";
import { ComparisonBranch } from "../api/comparison";

export type AuthStackParamList = {
  Login: { accountCreated?: boolean } | undefined;
  Signup: undefined;
};

export type ProfileStackParamList = {
  Profile: undefined;
};

export type AiCounselorDrawerParamList = {
  Chat: undefined;
};

export type PredictorStackParamList = {
  PredictorForm: undefined;
  PredictorResults: { predictionId: number; results: PredictorResult[] };
};

export type ComparisonStackParamList = {
  ComparisonForm: undefined;
  BranchPicker: { target: "branch1" | "branch2" };
  ComparisonResults: { comparisonId: number; branch1: ComparisonBranch; branch2: ComparisonBranch };
};

// Single-screen stack, matching ProfileStackParamList's shape -- kept
// purely for consistent header treatment across tabs. CollegeDetail is
// deliberately NOT registered here too; it stays registered exactly once,
// at AuthenticatedStackParamList, reachable from this tab the same way
// Predictor/Comparison/AI Counselor already reach it.
export type SavedStackParamList = {
  SavedCollegesList: undefined;
};

export type MainTabParamList = {
  PredictorTab: undefined;
  ComparisonTab: undefined;
  SavedTab: undefined;
  ProfileTab: undefined;
  AiCounselorTab: undefined;
};

// Wraps the tab bar so CollegeDetail is reachable via navigation.navigate()
// from any nested navigator (Predictor's stack, Comparison's stack, the
// Saved stack, and the AI Counselor drawer) without registering the
// screen in each of their own stacks separately.
export type AuthenticatedStackParamList = {
  Main: undefined;
  CollegeDetail: { collegeId: number };
};
