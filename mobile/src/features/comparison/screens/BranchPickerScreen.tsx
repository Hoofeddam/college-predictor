import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { useEffect, useState } from "react";
import { ActivityIndicator, FlatList, ListRenderItemInfo, Pressable, StyleSheet, Text, TextInput, View } from "react-native";

import { ComparisonBranch, getBranches } from "../../../api/comparison";
import { ApiError } from "../../../api/types";
import { colors } from "../../../constants/colors";
import { ComparisonStackParamList } from "../../../navigation/types";

interface Props {
  onSelect: (branch: ComparisonBranch) => void;
  excludeBranchId?: number;
}

function label(branch: ComparisonBranch) {
  return `${branch.college.name} — ${branch.branch_name}`;
}

// GET /comparison/branches has no query-param filtering server-side, so
// this fetches once on mount and filters client-side as the user types --
// a synchronous in-memory .filter(), not a debounced network search like
// the AI Counselor's conversation list (that debounce exists to protect a
// server endpoint that, here, doesn't exist).
export function BranchPickerScreen({ onSelect, excludeBranchId }: Props) {
  const navigation = useNavigation<NativeStackNavigationProp<ComparisonStackParamList>>();

  const [branches, setBranches] = useState<ComparisonBranch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");

  useEffect(() => {
    let cancelled = false;

    getBranches()
      .then((data) => {
        if (cancelled) return;
        setBranches(data.branches);
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err instanceof ApiError ? err.message : "Couldn't load branches. Please try again.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const filtered = branches
    .filter((branch) => branch.id !== excludeBranchId)
    .filter((branch) => label(branch).toLowerCase().includes(query.trim().toLowerCase()));

  function handleSelect(branch: ComparisonBranch) {
    onSelect(branch);
    navigation.goBack();
  }

  function renderItem({ item }: ListRenderItemInfo<ComparisonBranch>) {
    return (
      <Pressable
        testID="branch-picker-row"
        style={({ pressed }) => [styles.row, pressed && styles.rowPressed]}
        onPress={() => handleSelect(item)}
        android_ripple={{ color: colors.rippleOnLight }}
        accessibilityRole="button"
      >
        <Text style={styles.rowTitle}>{item.college.name}</Text>
        <Text style={styles.rowSubtitle}>{item.branch_name}</Text>
      </Pressable>
    );
  }

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator color={colors.primary} />
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.centered}>
        <Text style={styles.error}>{error}</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <TextInput
        testID="branch-picker-search"
        style={styles.searchInput}
        placeholder="Search colleges or branches..."
        placeholderTextColor={colors.textMuted}
        value={query}
        onChangeText={setQuery}
      />

      {filtered.length === 0 ? (
        <Text style={styles.emptyText}>No matching branches.</Text>
      ) : (
        <FlatList
          testID="branch-picker-list"
          data={filtered}
          keyExtractor={(item) => String(item.id)}
          renderItem={renderItem}
          contentContainerStyle={styles.list}
          keyboardShouldPersistTaps="handled"
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    padding: 16,
  },
  centered: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: colors.background,
    padding: 24,
  },
  error: {
    color: colors.danger,
    backgroundColor: colors.dangerTint,
    padding: 12,
    borderRadius: 6,
    textAlign: "center",
  },
  searchInput: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 6,
    padding: 12,
    fontSize: 16,
    color: colors.text,
    backgroundColor: colors.surface,
    marginBottom: 12,
  },
  emptyText: {
    color: colors.textMuted,
    fontSize: 14,
    textAlign: "center",
    marginTop: 24,
  },
  list: {
    gap: 4,
  },
  row: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    paddingHorizontal: 14,
    paddingVertical: 10,
  },
  rowPressed: {
    opacity: 0.7,
  },
  rowTitle: {
    fontSize: 14,
    fontWeight: "600",
    color: colors.text,
  },
  rowSubtitle: {
    fontSize: 13,
    color: colors.textMuted,
  },
});
