import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { useState } from "react";
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
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { login as loginApi } from "../../../api/auth";
import { ApiError } from "../../../api/types";
import { colors } from "../../../constants/colors";
import { AuthStackParamList } from "../../../navigation/types";
import { useAuthStore } from "../../../store/authStore";

type Props = NativeStackScreenProps<AuthStackParamList, "Login">;

export function LoginScreen({ navigation, route }: Props) {
  const login = useAuthStore((state) => state.login);
  // AuthStack has headerShown: false, so there's no header to supply top/
  // bottom safe-area padding the way every other screen in the app gets
  // for free from its own navigator. Falls back to the existing 24px
  // padding when the device inset is smaller (e.g. this sandbox's web
  // preview, where insets are always 0), so the layout is unchanged
  // anywhere it was already fine.
  const insets = useSafeAreaInsets();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const accountCreated = route.params?.accountCreated ?? false;

  const canSubmit = email.trim().length > 0 && password.length > 0 && !loading;

  async function handleSubmit() {
    setLoading(true);
    setError(null);

    try {
      const data = await loginApi(email.trim(), password);
      await login(data.access_token, data.refresh_token, data.user);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
      setLoading(false);
    }
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : Platform.OS === "android" ? "height" : undefined}
    >
      <ScrollView
        style={styles.flex}
        contentContainerStyle={[
          styles.content,
          { paddingTop: Math.max(24, insets.top), paddingBottom: Math.max(24, insets.bottom) },
        ]}
        keyboardShouldPersistTaps="handled"
      >
        <Text style={styles.title}>College Predictor</Text>
        <Text style={styles.subtitle}>Log in to continue</Text>

        {accountCreated && !error ? (
          <Text style={styles.success}>Account created. Log in to continue.</Text>
        ) : null}

        {error ? <Text style={styles.error}>{error}</Text> : null}

        <TextInput
          testID="login-email"
          style={styles.input}
          placeholder="Email"
          placeholderTextColor={colors.textMuted}
          autoCapitalize="none"
          autoComplete="email"
          keyboardType="email-address"
          value={email}
          onChangeText={setEmail}
        />

        <TextInput
          testID="login-password"
          style={styles.input}
          placeholder="Password"
          placeholderTextColor={colors.textMuted}
          autoCapitalize="none"
          autoComplete="password"
          secureTextEntry
          value={password}
          onChangeText={setPassword}
        />

        <Pressable
          testID="login-submit"
          style={({ pressed }) => [styles.button, !canSubmit && styles.buttonDisabled, pressed && styles.buttonPressed]}
          onPress={handleSubmit}
          disabled={!canSubmit}
          android_ripple={{ color: colors.rippleOnDark }}
          accessibilityRole="button"
        >
          {loading ? (
            <ActivityIndicator color={colors.surface} />
          ) : (
            <Text style={styles.buttonText}>Log In</Text>
          )}
        </Pressable>

        <Pressable
          testID="login-goto-signup"
          onPress={() => navigation.navigate("Signup")}
          style={({ pressed }) => pressed && styles.linkPressed}
          android_ripple={{ color: colors.rippleOnLight }}
          hitSlop={8}
          accessibilityRole="button"
        >
          <Text style={styles.link}>Don't have an account? Sign up</Text>
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
    flexGrow: 1,
    justifyContent: "center",
    padding: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: "700",
    color: colors.text,
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 15,
    color: colors.textMuted,
    marginBottom: 24,
  },
  error: {
    color: colors.danger,
    backgroundColor: colors.dangerTint,
    padding: 12,
    borderRadius: 6,
    marginBottom: 16,
    textAlign: "center",
  },
  success: {
    color: colors.success,
    backgroundColor: colors.successTint,
    padding: 12,
    borderRadius: 6,
    marginBottom: 16,
  },
  input: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 6,
    padding: 12,
    fontSize: 16,
    color: colors.text,
    backgroundColor: colors.surface,
    marginBottom: 12,
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
  linkPressed: {
    opacity: 0.6,
  },
  link: {
    color: colors.primary,
    textAlign: "center",
    marginTop: 20,
    fontSize: 14,
  },
});
