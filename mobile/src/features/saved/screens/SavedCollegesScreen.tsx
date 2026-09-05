import { useNavigation, useFocusEffect } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { useCallback, useRef, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  ListRenderItemInfo,
  Pressable,
  RefreshControl,
  StyleSheet,
  Text,
  View,
} from "react-native";

import { SavedCollege, getSavedColleges } from "../../../api/saved";
import { colors } from "../../../constants/colors";
import { formatFees } from "../../../utils/format";
import { AuthenticatedStackParamList } from "../../../navigation/types";
import { AppCard } from "../../../components/AppCard";
import { StatCell } from "../../../components/StatCell";
import { StatGrid } from "../../../components/StatGrid";

type Status = "loading" | "ready" | "error";

// getSavedColleges(false) below may be served entirely from the module
// cache (api/saved.ts) rather than a real network call -- e.g. if the
// user already visited a CollegeDetail screen this session, the cache is
// already warm and this "initial load" resolves instantly. That's a
// desirable side effect of the cache, not something worked around here.
export function SavedCollegesScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<AuthenticatedStackParamList>>();

  const [saved, setSaved] = useState<SavedCollege[] | null>(null);
  const [status, setStatus] = useState<Status>("loading");
  const [refreshing, setRefreshing] = useState(false);

  // Tracks whether we've ever had a *successful* load -- not just an
  // attempt -- so a failed first load keeps retrying with the full
  // loading/error treatment on every focus, rather than silently
  // "backgrounding" a retry the user has no visible sign of.
  const hasLoadedRef = useRef(false);

  function fetchSaved(mode: "initial" | "background" | "refresh") {
    if (mode === "initial") {
      setStatus("loading");
    }
    if (mode === "refresh") {
      setRefreshing(true);
    }

    getSavedColleges(mode !== "initial")
      .then((data) => {
        setSaved(data.saved);
        setStatus("ready");
        hasLoadedRef.current = true;
      })
      .catch(() => {
        // Background/refresh failures deliberately keep showing whatever
        // list is already on screen -- only a failed *initial* load (no
        // data to preserve) surfaces as a full error state.
        if (mode === "initial") {
          setStatus("error");
        }
      })
      .finally(() => {
        if (mode === "refresh") {
          setRefreshing(false);
        }
      });
  }

  // Empty deps deliberately -- this must stay a stable callback identity.
  // If it captured `saved`/re-created on every fetch, useFocusEffect would
  // re-run every time fetchSaved's own state update changed that
  // reference, causing a refresh loop. hasLoadedRef sidesteps that by not
  // needing to be a dependency at all.
  useFocusEffect(
    useCallback(() => {
      fetchSaved(hasLoadedRef.current ? "background" : "initial");
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])
  );

  function handlePullToRefresh() {
    fetchSaved("refresh");
  }

  function renderItem({ item }: ListRenderItemInfo<SavedCollege>) {
    return (
      <Pressable
        testID="saved-college-row"
        onPress={() => navigation.navigate("CollegeDetail", { collegeId: item.college.id })}
        style={({ pressed }) => pressed && styles.rowPressed}
        android_ripple={{ color: colors.rippleOnLight }}
        accessibilityRole="button"
      >
        <AppCard>
          <Text style={styles.title}>{item.college.name}</Text>
          {item.college.location || item.college.state ? (
            <Text style={styles.subtitle}>
              {[item.college.location, item.college.state].filter(Boolean).join(", ")}
            </Text>
          ) : null}

          <StatGrid>
            <StatCell label="NIRF Rank" value={item.college.nirf_rank} />
            <StatCell label="Fees" value={formatFees(item.college.fees)} />
            <StatCell label="Hostel Fees" value={formatFees(item.college.hostel_fees)} />
            <StatCell label="Website" value={item.college.website} />
          </StatGrid>
        </AppCard>
      </Pressable>
    );
  }

  if (status === "loading" && saved === null) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator color={colors.primary} />
      </View>
    );
  }

  if (status === "error" && saved === null) {
    return (
      <View style={styles.centered}>
        <Text style={styles.error}>Couldn't load your saved colleges. Please try again.</Text>
      </View>
    );
  }

  if (saved !== null && saved.length === 0) {
    return (
      <View style={styles.centered}>
        <Text style={styles.emptyText}>No saved colleges yet.</Text>
      </View>
    );
  }

  return (
    <FlatList
      testID="saved-colleges-list"
      style={styles.container}
      data={saved ?? []}
      keyExtractor={(item) => String(item.id)}
      renderItem={renderItem}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={handlePullToRefresh} />}
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
  emptyText: {
    color: colors.textMuted,
    fontSize: 15,
    textAlign: "center",
  },
  rowPressed: {
    opacity: 0.7,
  },
  title: {
    fontSize: 16,
    fontWeight: "700",
    color: colors.text,
  },
  subtitle: {
    fontSize: 13,
    color: colors.textMuted,
    marginBottom: 4,
  },
});
