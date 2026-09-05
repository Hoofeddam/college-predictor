import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { useEffect, useState } from "react";
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";

import { CollegeBranch, CollegeDetail, getCollege } from "../../../api/college";
import { getSavedColleges, saveCollege, unsaveCollege } from "../../../api/saved";
import { ApiError } from "../../../api/types";
import { colors } from "../../../constants/colors";
import { formatFees, formatPackage, formatPercentage } from "../../../utils/format";
import { AuthenticatedStackParamList } from "../../../navigation/types";
import { AppCard } from "../../../components/AppCard";
import { StatCell } from "../../../components/StatCell";
import { StatGrid } from "../../../components/StatGrid";

type Props = NativeStackScreenProps<AuthenticatedStackParamList, "CollegeDetail">;

// AppCard/StatGrid/StatCell -- was two local, near-duplicate copies of
// these until this migration (see src/components/AppCard.tsx's own
// comment on why they were promoted); this screen just predates that
// promotion and is now brought in line with it.
function BranchRow({ branch }: { branch: CollegeBranch }) {
  return (
    <AppCard>
      <Text style={styles.branchName}>{branch.branch_name}</Text>
      <StatGrid>
        <StatCell label="Avg Package" value={formatPackage(branch.avg_package)} />
        <StatCell label="Median Package" value={formatPackage(branch.median_package)} />
        <StatCell label="Placement Rate" value={formatPercentage(branch.placement_rate)} />
      </StatGrid>
    </AppCard>
  );
}

export function CollegeDetailScreen({ route }: Props) {
  const { collegeId } = route.params;

  const [college, setCollege] = useState<CollegeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Independent from the college fetch above -- a failure here shouldn't
  // block the rest of the screen. savedId doubles as both "is this
  // college saved" (non-null) and the id DELETE /saved/<saved_id> needs,
  // since that endpoint takes the saved row's id, not the college's.
  const [savedId, setSavedId] = useState<number | null>(null);
  const [savingInFlight, setSavingInFlight] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    getCollege(collegeId)
      .then((data) => {
        if (cancelled) return;
        setCollege(data.college);
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [collegeId]);

  useEffect(() => {
    let cancelled = false;

    // Uses the module-level cache in api/saved.ts (forceRefresh=false) --
    // if the Saved tab or another CollegeDetail visit already populated
    // it this session, this resolves with no network call at all. A
    // failure here just leaves savedId as null (button reads "Save"),
    // which is safe: POST /saved/<id> is idempotent, so worst case a
    // "Save" tap on an already-saved college just reconfirms it.
    getSavedColleges()
      .then((data) => {
        if (cancelled) return;
        const existing = data.saved.find((entry) => entry.college.id === collegeId);
        setSavedId(existing ? existing.id : null);
      })
      .catch(() => {
        // Silently leave savedId as null -- see comment above.
      });

    return () => {
      cancelled = true;
    };
  }, [collegeId]);

  async function handleToggleSave() {
    setSavingInFlight(true);

    try {
      if (savedId != null) {
        await unsaveCollege(savedId);
        setSavedId(null);
      } else {
        const data = await saveCollege(collegeId);
        setSavedId(data.saved.id);
      }
    } catch {
      // Leave savedId unchanged on failure -- the button simply stays in
      // its current state, matching how every other submit action in
      // this app fails (no toast/snackbar system exists to surface this
      // more prominently).
    } finally {
      setSavingInFlight(false);
    }
  }

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator color={colors.primary} />
      </View>
    );
  }

  if (error || !college) {
    return (
      <View style={styles.centered}>
        <Text style={styles.error}>{error ?? "College not found."}</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content} testID="college-detail-scroll">
      <Text style={styles.name} testID="college-detail-name">
        {college.name}
      </Text>
      {college.location || college.state ? (
        <Text style={styles.location}>
          {[college.location, college.state].filter(Boolean).join(", ")}
        </Text>
      ) : null}

      <StatGrid>
        <StatCell label="NIRF Rank" value={college.nirf_rank} />
        <StatCell label="Fees" value={formatFees(college.fees)} />
        <StatCell label="Hostel Fees" value={formatFees(college.hostel_fees)} />
        <StatCell label="Website" value={college.website} />
      </StatGrid>

      <Pressable
        testID="college-detail-save-toggle"
        style={({ pressed }) => [
          styles.saveButton,
          savedId != null && styles.saveButtonActive,
          pressed && styles.saveButtonPressed,
        ]}
        onPress={handleToggleSave}
        disabled={savingInFlight}
        android_ripple={{ color: savedId != null ? colors.rippleOnLight : colors.rippleOnDark }}
        accessibilityRole="button"
        accessibilityLabel={savedId != null ? "Remove from saved colleges" : "Save this college"}
        accessibilityState={{ busy: savingInFlight }}
      >
        {savingInFlight ? (
          <ActivityIndicator color={savedId != null ? colors.primary : colors.surface} />
        ) : (
          <Text style={[styles.saveButtonText, savedId != null && styles.saveButtonTextActive]}>
            {savedId != null ? "★ Saved" : "☆ Save College"}
          </Text>
        )}
      </Pressable>

      <Text style={styles.sectionTitle}>Branches</Text>

      {college.branches.length === 0 ? (
        <Text style={styles.emptyText}>No branch data available.</Text>
      ) : (
        <View style={styles.branchList}>
          {college.branches.map((branch) => (
            <BranchRow key={branch.id} branch={branch} />
          ))}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
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
  error: {
    color: colors.danger,
    backgroundColor: colors.dangerTint,
    padding: 12,
    borderRadius: 6,
    textAlign: "center",
  },
  name: {
    fontSize: 24,
    fontWeight: "700",
    color: colors.text,
  },
  saveButton: {
    backgroundColor: colors.primary,
    borderRadius: 6,
    padding: 14,
    alignItems: "center",
    marginTop: 16,
  },
  saveButtonActive: {
    backgroundColor: colors.brassTint,
  },
  saveButtonPressed: {
    opacity: 0.85,
  },
  saveButtonText: {
    color: colors.surface,
    fontSize: 15,
    fontWeight: "600",
  },
  saveButtonTextActive: {
    color: colors.brass,
  },
  location: {
    fontSize: 14,
    color: colors.textMuted,
    marginTop: 2,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: colors.text,
    marginTop: 12,
    marginBottom: 12,
  },
  emptyText: {
    color: colors.textMuted,
    fontSize: 14,
  },
  branchList: {
    gap: 12,
  },
  branchName: {
    fontSize: 15,
    fontWeight: "700",
    color: colors.text,
    marginBottom: 4,
  },
});
