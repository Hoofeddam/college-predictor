import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from "react-native";

import { ComparisonBranch, compare } from "../../../api/comparison";
import { ApiError } from "../../../api/types";
import { colors } from "../../../constants/colors";
import { ComparisonStackParamList } from "../../../navigation/types";

interface Props {
  navigation: NativeStackNavigationProp<ComparisonStackParamList, "ComparisonForm">;
  branch1: ComparisonBranch | null;
  branch2: ComparisonBranch | null;
  onSwap: () => void;
}

function BranchSlot({
  label,
  branch,
  testID,
  onPress,
}: {
  label: string;
  branch: ComparisonBranch | null;
  testID: string;
  onPress: () => void;
}) {
  return (
    <View style={styles.field}>
      <Text style={styles.label}>{label}</Text>
      <Pressable
        testID={testID}
        style={({ pressed }) => [styles.slot, pressed && styles.slotPressed]}
        onPress={onPress}
        android_ripple={{ color: colors.rippleOnLight }}
        accessibilityRole="button"
        accessibilityLabel={branch ? `${label}: ${branch.college.name}, ${branch.branch_name}` : `${label}: tap to select a branch`}
      >
        {branch ? (
          <>
            <Text style={styles.slotTitle}>{branch.college.name}</Text>
            <Text style={styles.slotSubtitle}>{branch.branch_name}</Text>
          </>
        ) : (
          <Text style={styles.slotPlaceholder}>Tap to select a branch</Text>
        )}
      </Pressable>
    </View>
  );
}

// branch1/branch2 arrive as props from ComparisonNavigator (lifted there,
// not local here -- see ComparisonNavigator.tsx). submitting/submitError
// stay local: nothing else needs them.
export function ComparisonFormScreen({ navigation, branch1, branch2, onSwap }: Props) {
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const canSubmit = Boolean(branch1 && branch2 && !submitting);

  async function handleSubmit() {
    if (!branch1 || !branch2) {
      return;
    }

    setSubmitting(true);
    setSubmitError(null);

    try {
      const data = await compare(branch1.id, branch2.id);
      navigation.navigate("ComparisonResults", {
        comparisonId: data.comparison_id,
        branch1: data.branch1,
        branch2: data.branch2,
      });
    } catch (err) {
      setSubmitError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Compare two branches</Text>
      <Text style={styles.subtitle}>
        See average package, placement rate, fees and NIRF rank side by side.
      </Text>

      {submitError ? <Text style={styles.error}>{submitError}</Text> : null}

      <BranchSlot
        label="First branch"
        branch={branch1}
        testID="comparison-branch1-slot"
        onPress={() => navigation.navigate("BranchPicker", { target: "branch1" })}
      />
      <BranchSlot
        label="Second branch"
        branch={branch2}
        testID="comparison-branch2-slot"
        onPress={() => navigation.navigate("BranchPicker", { target: "branch2" })}
      />

      {branch1 && branch2 ? (
        <Pressable
          testID="comparison-swap"
          style={({ pressed }) => [styles.swap, pressed && styles.swapPressed]}
          onPress={onSwap}
          android_ripple={{ color: colors.rippleOnLight }}
          hitSlop={8}
          accessibilityRole="button"
          accessibilityLabel="Swap first and second branch"
        >
          <Text style={styles.swapText}>⇅ Swap</Text>
        </Pressable>
      ) : null}

      <Pressable
        testID="comparison-submit"
        style={({ pressed }) => [styles.button, !canSubmit && styles.buttonDisabled, pressed && styles.buttonPressed]}
        onPress={handleSubmit}
        disabled={!canSubmit}
        android_ripple={{ color: colors.rippleOnDark }}
        accessibilityRole="button"
      >
        {submitting ? (
          <ActivityIndicator color={colors.surface} />
        ) : (
          <Text style={styles.buttonText}>Compare</Text>
        )}
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    padding: 20,
  },
  title: {
    fontSize: 22,
    fontWeight: "700",
    color: colors.text,
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    color: colors.textMuted,
    marginBottom: 20,
  },
  error: {
    color: colors.danger,
    backgroundColor: colors.dangerTint,
    padding: 12,
    borderRadius: 6,
    marginBottom: 16,
    textAlign: "center",
  },
  field: {
    marginBottom: 16,
  },
  label: {
    fontSize: 11,
    fontWeight: "700",
    letterSpacing: 0.5,
    textTransform: "uppercase",
    color: colors.textMuted,
    marginBottom: 8,
  },
  slot: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    padding: 14,
    backgroundColor: colors.surface,
  },
  slotTitle: {
    fontSize: 15,
    fontWeight: "600",
    color: colors.text,
  },
  slotSubtitle: {
    fontSize: 13,
    color: colors.textMuted,
  },
  slotPlaceholder: {
    fontSize: 14,
    color: colors.textMuted,
  },
  slotPressed: {
    opacity: 0.85,
  },
  swap: {
    alignSelf: "center",
    paddingVertical: 8,
    paddingHorizontal: 16,
    marginBottom: 8,
  },
  swapPressed: {
    opacity: 0.6,
  },
  swapText: {
    fontSize: 14,
    fontWeight: "600",
    color: colors.primary,
  },
  button: {
    backgroundColor: colors.primary,
    borderRadius: 6,
    padding: 14,
    alignItems: "center",
    marginTop: 8,
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  buttonPressed: {
    opacity: 0.85,
  },
  buttonText: {
    color: colors.surface,
    fontSize: 16,
    fontWeight: "600",
  },
});
