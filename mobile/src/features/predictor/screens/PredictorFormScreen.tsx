import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import { PredictorOption, getOptions, predict } from "../../../api/predictor";
import { ApiError } from "../../../api/types";
import { colors } from "../../../constants/colors";
import { PredictorStackParamList } from "../../../navigation/types";

type Props = NativeStackScreenProps<PredictorStackParamList, "PredictorForm">;

// Options are small, closed sets (5 exams, 5 categories, 3 quotas in the
// real dataset) -- a chip selector covers this fully with no native
// dependency, unlike a real <Picker> which would need one just for 3-5
// items per field. Used 3 times in this one screen; not promoted anywhere
// since nothing outside this screen needs it.
function ChipGroup({
  label,
  options,
  selected,
  onSelect,
  testIDPrefix,
}: {
  label: string;
  options: PredictorOption[];
  selected: string | null;
  onSelect: (name: string) => void;
  testIDPrefix: string;
}) {
  return (
    <View style={styles.field}>
      <Text style={styles.label}>{label}</Text>
      <View style={styles.chipRow}>
        {options.map((option) => {
          const isSelected = option.name === selected;
          return (
            <Pressable
              key={option.id}
              testID={`${testIDPrefix}-${option.name}`}
              style={({ pressed }) => [styles.chip, isSelected && styles.chipSelected, pressed && styles.chipPressed]}
              onPress={() => onSelect(option.name)}
              android_ripple={{ color: isSelected ? colors.rippleOnDark : colors.rippleOnLight }}
              accessibilityRole="button"
              accessibilityState={{ selected: isSelected }}
            >
              <Text style={[styles.chipText, isSelected && styles.chipTextSelected]}>
                {option.name}
              </Text>
            </Pressable>
          );
        })}
      </View>
    </View>
  );
}

export function PredictorFormScreen({ navigation }: Props) {
  const [exams, setExams] = useState<PredictorOption[]>([]);
  const [categories, setCategories] = useState<PredictorOption[]>([]);
  const [quotas, setQuotas] = useState<PredictorOption[]>([]);
  const [optionsLoading, setOptionsLoading] = useState(true);
  const [optionsError, setOptionsError] = useState<string | null>(null);

  const [exam, setExam] = useState<string | null>(null);
  const [category, setCategory] = useState<string | null>(null);
  const [quota, setQuota] = useState<string | null>(null);
  const [rank, setRank] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    getOptions()
      .then((data) => {
        if (cancelled) return;
        setExams(data.exams);
        setCategories(data.categories);
        setQuotas(data.quotas);
      })
      .catch((err) => {
        if (cancelled) return;
        setOptionsError(err instanceof ApiError ? err.message : "Couldn't load options. Please try again.");
      })
      .finally(() => {
        if (!cancelled) setOptionsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const parsedRank = Number.parseInt(rank.trim(), 10);
  const rankIsValid = rank.trim().length > 0 && Number.isInteger(parsedRank) && parsedRank > 0;
  const canSubmit = Boolean(exam && category && quota && rankIsValid && !submitting);

  async function handleSubmit() {
    if (!exam || !category || !quota || !rankIsValid) {
      return;
    }

    setSubmitting(true);
    setSubmitError(null);

    try {
      const data = await predict(exam, category, quota, parsedRank);
      navigation.navigate("PredictorResults", {
        predictionId: data.prediction_id,
        results: data.results,
      });
    } catch (err) {
      setSubmitError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  if (optionsLoading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator color={colors.primary} />
      </View>
    );
  }

  if (optionsError) {
    return (
      <View style={styles.centered}>
        <Text style={styles.error}>{optionsError}</Text>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : Platform.OS === "android" ? "height" : undefined}
    >
      <ScrollView
        style={styles.flex}
        contentContainerStyle={styles.content}
        keyboardShouldPersistTaps="handled"
      >
      <Text style={styles.title}>Find your eligible colleges</Text>
      <Text style={styles.subtitle}>
        Enter your exam, category, quota and rank to see which colleges and branches you're likely
        eligible for.
      </Text>

      {submitError ? <Text style={styles.error}>{submitError}</Text> : null}

      <ChipGroup label="Exam" options={exams} selected={exam} onSelect={setExam} testIDPrefix="predictor-exam" />
      <ChipGroup
        label="Category"
        options={categories}
        selected={category}
        onSelect={setCategory}
        testIDPrefix="predictor-category"
      />
      <ChipGroup label="Quota" options={quotas} selected={quota} onSelect={setQuota} testIDPrefix="predictor-quota" />

      <View style={styles.field}>
        <Text style={styles.label}>Rank</Text>
        <TextInput
          testID="predictor-rank"
          style={styles.input}
          placeholder="Enter your rank"
          placeholderTextColor={colors.textMuted}
          keyboardType="number-pad"
          value={rank}
          onChangeText={setRank}
        />
      </View>

      <Pressable
        testID="predictor-submit"
        style={({ pressed }) => [styles.button, !canSubmit && styles.buttonDisabled, pressed && styles.buttonPressed]}
        onPress={handleSubmit}
        disabled={!canSubmit}
        android_ripple={{ color: colors.rippleOnDark }}
        accessibilityRole="button"
      >
        {submitting ? (
          <ActivityIndicator color={colors.surface} />
        ) : (
          <Text style={styles.buttonText}>Predict</Text>
        )}
      </Pressable>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  flex: {
    flex: 1,
  },
  content: {
    padding: 20,
  },
  centered: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: colors.background,
    padding: 24,
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
    marginBottom: 18,
  },
  label: {
    fontSize: 11,
    fontWeight: "700",
    letterSpacing: 0.5,
    textTransform: "uppercase",
    color: colors.textMuted,
    marginBottom: 8,
  },
  chipRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  chip: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    paddingHorizontal: 14,
    paddingVertical: 8,
    backgroundColor: colors.surface,
  },
  chipSelected: {
    borderColor: colors.primary,
    backgroundColor: colors.primary,
  },
  chipText: {
    fontSize: 14,
    color: colors.text,
  },
  chipTextSelected: {
    color: colors.surface,
    fontWeight: "600",
  },
  chipPressed: {
    opacity: 0.85,
  },
  input: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 6,
    padding: 12,
    fontSize: 16,
    color: colors.text,
    backgroundColor: colors.surface,
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
