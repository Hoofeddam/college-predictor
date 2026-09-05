import { ReactNode } from "react";
import { StyleSheet, Text, View } from "react-native";

import { colors } from "../constants/colors";

interface AppCardProps {
  eyebrow?: string;
  children: ReactNode;
}

// Promoted from features/ai-counselor/components/blocks/BlockCard.tsx once
// Predictor's own PredictionResultCard turned out to be a byte-for-byte
// match (same padding/border/radius values) -- a genuine second consumer,
// not a speculative abstraction. Named AppCard, not Card, so this stays
// unambiguous as the shared components folder grows. No footer/action
// slot: consumers own their own actions (e.g. "View Details") directly,
// rather than routing them through this generic container.
export function AppCard({ eyebrow, children }: AppCardProps) {
  return (
    <View style={styles.card}>
      {eyebrow ? <Text style={styles.eyebrow}>{eyebrow}</Text> : null}
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    padding: 14,
  },
  eyebrow: {
    fontSize: 11,
    fontWeight: "700",
    letterSpacing: 0.5,
    textTransform: "uppercase",
    color: colors.brass,
    marginBottom: 8,
  },
});
