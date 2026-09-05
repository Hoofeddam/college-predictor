import { StyleSheet, Text, View } from "react-native";

import { colors } from "../constants/colors";

interface TagProps {
  text: string;
  accent?: boolean;
}

// Promoted after showing up as two independent, near-identical inline
// copies (features/ai-counselor/components/blocks/PredictionCard.tsx and
// features/predictor/components/PredictionResultCard.tsx) -- same
// evidence-based promotion as AppCard/StatGrid/StatCell.
export function Tag({ text, accent }: TagProps) {
  return (
    <View style={[styles.tag, accent && styles.tagAccent]}>
      <Text style={[styles.tagText, accent && styles.tagTextAccent]}>{text}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  tag: {
    borderWidth: 1,
    borderColor: colors.borderStrong,
    borderRadius: 5,
    paddingHorizontal: 8,
    paddingVertical: 3,
  },
  tagAccent: {
    borderColor: "transparent",
    backgroundColor: colors.brassTint,
  },
  tagText: {
    fontSize: 11,
    fontWeight: "600",
    color: colors.textMuted,
  },
  tagTextAccent: {
    color: colors.brass,
  },
});
