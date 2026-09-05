import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { PredictorResult } from "../../../api/predictor";
import { colors } from "../../../constants/colors";
import { formatFees, formatPackage, formatPercentage } from "../../../utils/format";
import { AuthenticatedStackParamList } from "../../../navigation/types";
import { AppCard } from "../../../components/AppCard";
import { StatCell } from "../../../components/StatCell";
import { StatGrid } from "../../../components/StatGrid";
import { Tag } from "../../../components/Tag";

export function PredictionResultCard({ result }: { result: PredictorResult }) {
  const navigation = useNavigation<NativeStackNavigationProp<AuthenticatedStackParamList>>();

  return (
    <AppCard>
      <View style={styles.top}>
        <View style={styles.titleBlock}>
          <Text style={styles.title}>{result.college}</Text>
          <Text style={styles.subtitle}>{result.branch}</Text>
        </View>
        <View style={styles.tagRow}>
          <Tag text={result.exam} />
          <Tag text={`${result.category} · ${result.quota}`} />
          {result.nirf_rank ? <Tag text={`NIRF #${result.nirf_rank}`} accent /> : null}
        </View>
      </View>

      <Text style={styles.meta}>
        Round {result.round}, {result.year}
      </Text>

      <StatGrid>
        <StatCell label="Closing Rank" value={result.closing_rank} />
        <StatCell label="Avg Package" value={formatPackage(result.avg_package)} />
        <StatCell label="Median Package" value={formatPackage(result.median_package)} />
        <StatCell label="Placement Rate" value={formatPercentage(result.placement_rate)} />
        <StatCell label="Fees" value={formatFees(result.fees)} />
        <StatCell label="Hostel Fees" value={formatFees(result.hostel_fees)} />
      </StatGrid>

      <Pressable
        testID="prediction-result-view-details"
        style={({ pressed }) => [styles.viewDetails, pressed && styles.viewDetailsPressed]}
        onPress={() => navigation.navigate("CollegeDetail", { collegeId: result.college_id })}
        android_ripple={{ color: colors.rippleOnLight }}
        accessibilityRole="button"
      >
        <Text style={styles.viewDetailsText}>View Details →</Text>
      </Pressable>
    </AppCard>
  );
}

const styles = StyleSheet.create({
  top: {
    marginBottom: 4,
  },
  titleBlock: {
    marginBottom: 6,
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
  tagRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
  },
  meta: {
    fontSize: 12,
    color: colors.textFaint,
    marginBottom: 8,
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
