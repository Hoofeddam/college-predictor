import { useEffect, useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from "react-native";

import { getProfile } from "../../../api/profile";
import { ApiError, User } from "../../../api/types";
import { colors } from "../../../constants/colors";
import { useAuthStore } from "../../../store/authStore";

export function ProfileScreen() {
  const storedUser = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  const [profile, setProfile] = useState<User | null>(storedUser);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    getProfile()
      .then((data) => {
        if (!cancelled) {
          setProfile(data.user);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof ApiError ? err.message : "Something went wrong.");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Profile</Text>

      {loading && !profile ? <ActivityIndicator color={colors.primary} /> : null}

      {error ? <Text style={styles.error}>{error}</Text> : null}

      {profile ? (
        <View style={styles.card} testID="profile-card">
          <View style={styles.field}>
            <Text style={styles.label}>Username</Text>
            <Text style={styles.value} testID="profile-username">{profile.username}</Text>
          </View>
          <View style={styles.field}>
            <Text style={styles.label}>Email</Text>
            <Text style={styles.value} testID="profile-email">{profile.email}</Text>
          </View>
        </View>
      ) : null}

      <Pressable
        testID="profile-logout"
        style={({ pressed }) => [styles.button, pressed && styles.buttonPressed]}
        onPress={() => logout()}
        android_ripple={{ color: colors.rippleOnLight }}
        accessibilityRole="button"
      >
        <Text style={styles.buttonText}>Log Out</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    padding: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: "700",
    color: colors.text,
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
  card: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    padding: 16,
    marginBottom: 24,
  },
  field: {
    marginBottom: 12,
  },
  label: {
    fontSize: 11,
    fontWeight: "600",
    letterSpacing: 0.5,
    textTransform: "uppercase",
    color: colors.textMuted,
    marginBottom: 2,
  },
  value: {
    fontSize: 16,
    color: colors.text,
  },
  button: {
    borderWidth: 1,
    borderColor: colors.danger,
    borderRadius: 6,
    padding: 14,
    alignItems: "center",
  },
  buttonPressed: {
    opacity: 0.7,
  },
  buttonText: {
    color: colors.danger,
    fontSize: 16,
    fontWeight: "600",
  },
});
