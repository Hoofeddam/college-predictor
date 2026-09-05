import { ReactNode, useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { colors } from "../../../../constants/colors";

interface BlockDetailsProps {
  summary: string;
  children: ReactNode;
}

// RN has no native <details> -- a Pressable + local useState toggle is
// enough; no animation library needed for a plain show/hide.
export function BlockDetails({ summary, children }: BlockDetailsProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <View style={styles.container}>
      <Pressable
        style={({ pressed }) => [styles.summaryButton, pressed && styles.summaryButtonPressed]}
        onPress={() => setExpanded((value) => !value)}
        android_ripple={{ color: colors.rippleOnLight }}
        hitSlop={8}
        accessibilityRole="button"
        accessibilityLabel={summary}
        accessibilityState={{ expanded }}
      >
        <Text style={styles.summary}>
          {expanded ? "▾" : "▸"} {summary}
        </Text>
      </Pressable>
      {expanded ? <View style={styles.content}>{children}</View> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginTop: 10,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  summaryButton: {
    paddingVertical: 4,
  },
  summaryButtonPressed: {
    opacity: 0.6,
  },
  summary: {
    fontSize: 13,
    fontWeight: "600",
    color: colors.primary,
  },
  content: {
    marginTop: 8,
  },
});
