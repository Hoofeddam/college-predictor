import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { ComparisonBranch } from "../../../api/comparison";
import { colors } from "../../../constants/colors";
import { formatFees, formatPackage, formatPercentage } from "../../../utils/format";
import { AuthenticatedStackParamList } from "../../../navigation/types";
import { AppCard } from "../../../components/AppCard";
import { StatCell } from "../../../components/StatCell";
import { StatGrid } from "../../../components/StatGrid";

// Stacked vertically (branch1 then branch2), not side-by-side -- matching
// the web app's own mobile breakpoint behavior and the AI Counselor's
// ComparisonCard, which already stacks for the same reason. All stats
// shown flat, no collapsible section -- matches both compare_result.html
// (a single always-visible table) and Predictor's own established
// full-page precedent (PredictionResultCard), rather than the chat-bubble
// specific BlockDetails treatment.
function ComparisonColumn({ branch, testID }: { branch: ComparisonBranch; testID: string }) {
  const navigation = useNavigation<NativeStackNavigationProp<AuthenticatedStackParamList>>();

  return (
    <View style={styles.column}>
      <Text style={styles.title}>{branch.college.name}</Text>
      <Text style={styles.subtitle}>{branch.branch_name}</Text>
      {branch.college.location || branch.college.state ? (
        <Text style={styles.location}>
          {[branch.college.location, branch.college.state].filter(Boolean).join(", ")}
        </Text>
      ) : null}

      <StatGrid>
        <StatCell label="Avg Package" value={formatPackage(branch.avg_package)} />
        <StatCell label="Median Package" value={formatPackage(branch.median_package)} />
        <StatCell label="Placement Rate" value={formatPercentage(branch.placement_rate)} />
        <StatCell label="NIRF Rank" value={branch.college.nirf_rank} />
        <StatCell label="Fees" value={formatFees(branch.college.fees)} />
        <StatCell label="Hostel Fees" value={formatFees(branch.college.hostel_fees)} />
      </StatGrid>

      <Pressable
        testID={testID}
        style={({ pressed }) => [styles.viewDetails, pressed && styles.viewDetailsPressed]}
        onPress={() => navigation.navigate("CollegeDetail", { collegeId: branch.college.id })}
        android_ripple={{ color: colors.rippleOnLight }}
        accessibilityRole="button"
      >
        <Text style={styles.viewDetailsText}>View Details →</Text>
      </Pressable>
    </View>
  );
}

export function ComparisonResultCard({
  branch1,
  branch2,
}: {
  branch1: ComparisonBranch;
  branch2: ComparisonBranch;
}) {
  return (
    <AppCard>
      <ComparisonColumn branch={branch1} testID="comparison-result-view-details-1" />
      <View style={styles.divider} />
      <ComparisonColumn branch={branch2} testID="comparison-result-view-details-2" />
    </AppCard>
  );
}

const styles = StyleSheet.create({
  column: {
    marginBottom: 4,
  },
  divider: {
    height: 1,
    backgroundColor: colors.border,
    marginVertical: 12,
  },
  title: {
    fontSize: 16,
    fontWeight: "700",
    color: colors.text,
  },
  subtitle: {
    fontSize: 13,
    color: colors.textMuted,
  },
  location: {
    fontSize: 12,
    color: colors.textFaint,
    marginBottom: 4,
  },
  viewDetails: {
    marginTop: 6,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  viewDetailsPressed: {
    opacity: 0.6,
  },
  viewDetailsText: {
    fontSize: 13,
    fontWeight: "600",
    color: colors.primary,
  },
});
