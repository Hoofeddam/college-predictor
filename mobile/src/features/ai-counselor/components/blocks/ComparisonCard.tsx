import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { ResponseBlock } from "../../../../api/ai";
import { colors } from "../../../../constants/colors";
import { formatFees, formatPackage, formatPercentage } from "../../../../utils/format";
import { AuthenticatedStackParamList } from "../../../../navigation/types";
import { AppCard } from "../../../../components/AppCard";
import { StatCell } from "../../../../components/StatCell";
import { StatGrid } from "../../../../components/StatGrid";
import { BlockDetails } from "./BlockDetails";
import { ComparisonBranchData, ComparisonCardData } from "./types";

// Stacked vertically, not side-by-side -- matching the web app's own
// mobile breakpoint behavior (main.css collapses this same comparison
// grid to a single column under 768px; mobile is always at that width).
function ComparisonColumn({ data, testID }: { data: ComparisonBranchData; testID: string }) {
  const navigation = useNavigation<NativeStackNavigationProp<AuthenticatedStackParamList>>();

  return (
    <View style={styles.column}>
      <Text style={styles.title}>{data.college ?? "Unknown college"}</Text>
      {data.branch ? <Text style={styles.subtitle}>{data.branch}</Text> : null}

      <StatGrid>
        <StatCell label="Avg Package" value={formatPackage(data.avg_package)} />
        <StatCell label="Placement Rate" value={formatPercentage(data.placement_rate)} />
        <StatCell label="NIRF Rank" value={data.nirf_rank} />
      </StatGrid>

      <BlockDetails summary="Fees & more">
        <StatGrid>
          <StatCell label="Median Package" value={formatPackage(data.median_package)} />
          <StatCell label="Fees" value={formatFees(data.fees)} />
          <StatCell label="Hostel Fees" value={formatFees(data.hostel_fees)} />
        </StatGrid>
      </BlockDetails>

      {data.college_id != null ? (
        <Pressable
          testID={testID}
          style={({ pressed }) => [styles.viewDetails, pressed && styles.viewDetailsPressed]}
          onPress={() => navigation.navigate("CollegeDetail", { collegeId: data.college_id as number })}
          android_ripple={{ color: colors.rippleOnLight }}
          accessibilityRole="button"
        >
          <Text style={styles.viewDetailsText}>View Details →</Text>
        </Pressable>
      ) : null}
    </View>
  );
}

// BlockList already guarantees a supported type/version and a truthy
// `data` before this renders -- no defensive checks needed here, just
// presentation.
export function ComparisonCard({ block }: { block: ResponseBlock }) {
  const data = block.data as ComparisonCardData;

  return (
    <AppCard eyebrow="Comparison">
      <ComparisonColumn data={data.branch_1} testID="comparison-card-view-details-1" />
      <View style={styles.divider} />
      <ComparisonColumn data={data.branch_2} testID="comparison-card-view-details-2" />
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
    marginBottom: 4,
  },
  viewDetails: {
    marginTop: 10,
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
