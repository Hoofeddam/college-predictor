import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { FlatList, ListRenderItemInfo, StyleSheet, Text, View } from "react-native";

import { PredictorResult } from "../../../api/predictor";
import { colors } from "../../../constants/colors";
import { PredictorStackParamList } from "../../../navigation/types";
import { PredictionResultCard } from "../components/PredictionResultCard";

type Props = NativeStackScreenProps<PredictorStackParamList, "PredictorResults">;

// results/predictionId arrive as navigation params, not a re-fetch --
// POST /predictor/predict isn't idempotent (writes a new PredictionHistory
// row every call, confirmed in routes/api/predictor.py), so this screen
// must not re-trigger it. The form already resolved the results once.
export function PredictorResultsScreen({ route }: Props) {
  const { results } = route.params;

  function renderItem({ item }: ListRenderItemInfo<PredictorResult>) {
    return <PredictionResultCard result={item} />;
  }

  if (results.length === 0) {
    return (
      <View style={styles.emptyState}>
        <Text style={styles.emptyText}>No colleges found for the selected criteria.</Text>
      </View>
    );
  }

  return (
    <FlatList
      testID="predictor-results-list"
      style={styles.container}
      data={results}
      keyExtractor={(item, index) => `${item.college_id}-${item.branch}-${item.round}-${index}`}
      renderItem={renderItem}
      contentContainerStyle={styles.content}
    />
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: 16,
    gap: 12,
  },
  emptyState: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: colors.background,
    padding: 24,
  },
  emptyText: {
    color: colors.textMuted,
    fontSize: 15,
    textAlign: "center",
  },
});
