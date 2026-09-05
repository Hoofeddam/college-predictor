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

import { signup as signupApi } from "../../../api/auth";
import { ApiError } from "../../../api/types";
import { colors } from "../../../constants/colors";
import { AuthStackParamList } from "../../../navigation/types";

type Props = NativeStackScreenProps<AuthStackParamList, "Signup">;

export function SignupScreen({ navigation }: Props) {
  // Same reasoning as LoginScreen: AuthStack has headerShown: false, so
  // this screen gets no free safe-area padding from a header the way
  // every other screen in the app does.
  const insets = useSafeAreaInsets();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSubmit =
    username.trim().length > 0 && email.trim().length > 0 && password.length > 0 && !loading;

  async function handleSubmit() {
    setLoading(true);
    setError(null);

    try {
      // Signup returns only { user }, no tokens -- log in separately.
      await signupApi(username.trim(), email.trim(), password);
      navigation.replace("Login", { accountCreated: true });
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
        <Text style={styles.title}>Create account</Text>
        <Text style={styles.subtitle}>Get started with College Predictor</Text>

        {error ? <Text style={styles.error}>{error}</Text> : null}

        <TextInput
          testID="signup-username"
          style={styles.input}
          placeholder="Username"
          placeholderTextColor={colors.textMuted}
          autoCapitalize="none"
          autoComplete="username"
          value={username}
          onChangeText={setUsername}
        />

        <TextInput
          testID="signup-email"
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
          testID="signup-password"
          style={styles.input}
          placeholder="Password"
          placeholderTextColor={colors.textMuted}
          autoCapitalize="none"
          autoComplete="password-new"
          secureTextEntry
          value={password}
          onChangeText={setPassword}
        />

        <Pressable
          testID="signup-submit"
          style={({ pressed }) => [styles.button, !canSubmit && styles.buttonDisabled, pressed && styles.buttonPressed]}
          onPress={handleSubmit}
          disabled={!canSubmit}
          android_ripple={{ color: colors.rippleOnDark }}
          accessibilityRole="button"
        >
          {loading ? (
            <ActivityIndicator color={colors.surface} />
          ) : (
            <Text style={styles.buttonText}>Sign Up</Text>
          )}
        </Pressable>

        <Pressable
          testID="signup-goto-login"
          onPress={() => navigation.navigate("Login")}
          style={({ pressed }) => pressed && styles.linkPressed}
          android_ripple={{ color: colors.rippleOnLight }}
          hitSlop={8}
          accessibilityRole="button"
        >
          <Text style={styles.link}>Already have an account? Log in</Text>
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
