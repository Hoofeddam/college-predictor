import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { Pressable, StyleSheet, Text } from "react-native";

import { ResponseBlock } from "../../../../api/ai";
import { colors } from "../../../../constants/colors";
import { formatFees, formatPackage, formatPercentage } from "../../../../utils/format";
import { AuthenticatedStackParamList } from "../../../../navigation/types";
import { AppCard } from "../../../../components/AppCard";
import { StatCell } from "../../../../components/StatCell";
import { StatGrid } from "../../../../components/StatGrid";
import { BlockDetails } from "./BlockDetails";
import { RecommendationCardData } from "./types";

// BlockList already guarantees a supported type/version and a truthy
// `data` before this renders -- no defensive checks needed here, just
// presentation. AppCard itself stays a plain container -- this card
// owns its own "View Details" action and navigation call rather than
// routing it through a generic footer prop.
export function RecommendationCard({ block }: { block: ResponseBlock }) {
  const data = block.data as RecommendationCardData;
  const navigation = useNavigation<NativeStackNavigationProp<AuthenticatedStackParamList>>();

  return (
    <AppCard>
      <Text style={styles.title}>{data.college_name ?? "Unknown college"}</Text>
      {data.branch ? <Text style={styles.subtitle}>{data.branch}</Text> : null}

      <StatGrid>
        <StatCell label="Closing Rank" value={data.closing_rank} />
        <StatCell label="Avg Package" value={formatPackage(data.avg_package)} />
        <StatCell label="Placement Rate" value={formatPercentage(data.placement_rate)} />
        <StatCell label="NIRF Rank" value={data.nirf_rank} />
      </StatGrid>

      <BlockDetails summary="Fees & more">
        <StatGrid>
          <StatCell label="Fees" value={formatFees(data.fees)} />
          <StatCell label="Hostel Fees" value={formatFees(data.hostel_fees)} />
          <StatCell label="Website" value={data.website} />
        </StatGrid>
      </BlockDetails>

      {data.college_id != null ? (
        <Pressable
          testID="recommendation-card-view-details"
          style={({ pressed }) => [styles.viewDetails, pressed && styles.viewDetailsPressed]}
          onPress={() => navigation.navigate("CollegeDetail", { collegeId: data.college_id as number })}
          android_ripple={{ color: colors.rippleOnLight }}
          accessibilityRole="button"
        >
          <Text style={styles.viewDetailsText}>View Details →</Text>
        </Pressable>
      ) : null}
    </AppCard>
  );
}

const styles = StyleSheet.create({
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
