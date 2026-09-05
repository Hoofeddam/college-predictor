import { colors } from "./colors";

// Shared across every navigator that shows a header (PredictorNavigator,
// ComparisonNavigator, SavedNavigator, ProfileNavigator, AiCounselorNavigator's
// drawer, and the root AuthenticatedStack's CollegeDetail screen) so headers
// match the app's own navy/brass palette instead of React Navigation's
// stock default appearance. Not applied to AuthStack (Login/Signup), which
// deliberately has no header at all.
export const headerScreenOptions = {
  headerStyle: { backgroundColor: colors.primary },
  headerTintColor: colors.surface,
  headerTitleStyle: { fontWeight: "700" as const },
};
