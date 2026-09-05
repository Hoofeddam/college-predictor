import { StyleSheet, Text, View } from "react-native";

import { colors } from "../constants/colors";

interface StatCellProps {
  label: string;
  value: string | number | null | undefined;
}

// Promoted from features/ai-counselor/components/blocks/StatCell.tsx --
// see AppCard.tsx for the promotion rationale.
export function StatCell({ label, value }: StatCellProps) {
  return (
    <View style={styles.cell}>
      <Text style={styles.label}>{label}</Text>
      <Text style={styles.value}>{value != null ? String(value) : "—"}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  cell: {
    minWidth: "45%",
    marginBottom: 8,
  },
  label: {
    fontSize: 10,
    fontWeight: "700",
    letterSpacing: 0.5,
    textTransform: "uppercase",
    color: colors.textFaint,
    marginBottom: 2,
  },
  value: {
    fontSize: 15,
    color: colors.text,
  },
});
