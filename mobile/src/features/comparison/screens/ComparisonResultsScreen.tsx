import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { ScrollView, StyleSheet } from "react-native";

import { colors } from "../../../constants/colors";
import { ComparisonStackParamList } from "../../../navigation/types";
import { ComparisonResultCard } from "../components/ComparisonResultCard";

type Props = NativeStackScreenProps<ComparisonStackParamList, "ComparisonResults">;

// branch1/branch2/comparisonId arrive as navigation params, not a
// re-fetch -- POST /comparison/compare isn't idempotent (writes a new
// ComparisonHistory row every call, confirmed in routes/api/comparison.py),
// so this screen must not re-trigger it. The form already resolved the
// comparison once. Same reasoning as PredictorResultsScreen.
export function ComparisonResultsScreen({ route }: Props) {
  const { branch1, branch2 } = route.params;

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <ComparisonResultCard branch1={branch1} branch2={branch2} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: 16,
  },
});
