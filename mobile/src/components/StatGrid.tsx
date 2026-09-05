import { ReactNode } from "react";
import { StyleSheet, View } from "react-native";

import { colors } from "../constants/colors";

// Promoted from features/ai-counselor/components/blocks/StatGrid.tsx --
// see AppCard.tsx for the promotion rationale.
export function StatGrid({ children }: { children: ReactNode }) {
  return <View style={styles.grid}>{children}</View>;
}

const styles = StyleSheet.create({
  grid: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-between",
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
});
