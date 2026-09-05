import { Ionicons } from "@expo/vector-icons";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { useEffect } from "react";
import { ActivityIndicator, StyleSheet, View } from "react-native";

import { LoginScreen } from "../features/auth/screens/LoginScreen";
import { SignupScreen } from "../features/auth/screens/SignupScreen";
import { AiCounselorNavigator } from "../features/ai-counselor/AiCounselorNavigator";
import { CollegeDetailScreen } from "../features/college/screens/CollegeDetailScreen";
import { ComparisonNavigator } from "../features/comparison/ComparisonNavigator";
import { PredictorNavigator } from "../features/predictor/PredictorNavigator";
import { ProfileScreen } from "../features/profile/screens/ProfileScreen";
import { SavedNavigator } from "../features/saved/SavedNavigator";
import { colors } from "../constants/colors";
import { headerScreenOptions } from "../constants/navigationTheme";
import { useAuthStore } from "../store/authStore";
import {
  AuthenticatedStackParamList,
  AuthStackParamList,
  MainTabParamList,
  ProfileStackParamList,
} from "./types";

const AuthStack = createNativeStackNavigator<AuthStackParamList>();
const ProfileStack = createNativeStackNavigator<ProfileStackParamList>();
const MainTab = createBottomTabNavigator<MainTabParamList>();
const AuthenticatedStack = createNativeStackNavigator<AuthenticatedStackParamList>();

function AuthNavigator() {
  return (
    <AuthStack.Navigator screenOptions={{ headerShown: false }}>
      <AuthStack.Screen name="Login" component={LoginScreen} />
      <AuthStack.Screen name="Signup" component={SignupScreen} />
    </AuthStack.Navigator>
  );
}

function ProfileNavigator() {
  return (
    <ProfileStack.Navigator screenOptions={headerScreenOptions}>
      <ProfileStack.Screen name="Profile" component={ProfileScreen} />
    </ProfileStack.Navigator>
  );
}

// icon/iconOutline pairs per tab -- Ionicons ships bundled with Expo, no new
// native dependency beyond the @expo/vector-icons package itself.
const TAB_ICONS: Record<keyof MainTabParamList, { active: keyof typeof Ionicons.glyphMap; inactive: keyof typeof Ionicons.glyphMap }> = {
  PredictorTab: { active: "calculator", inactive: "calculator-outline" },
  ComparisonTab: { active: "git-compare", inactive: "git-compare-outline" },
  SavedTab: { active: "bookmark", inactive: "bookmark-outline" },
  AiCounselorTab: { active: "chatbubble-ellipses", inactive: "chatbubble-ellipses-outline" },
  ProfileTab: { active: "person", inactive: "person-outline" },
};

function makeTabBarIcon(tab: keyof MainTabParamList) {
  return ({ color, size, focused }: { color: string; size: number; focused: boolean }) => (
    <Ionicons name={focused ? TAB_ICONS[tab].active : TAB_ICONS[tab].inactive} size={size} color={color} />
  );
}

function MainNavigator() {
  return (
    <MainTab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textFaint,
      }}
    >
      <MainTab.Screen
        name="PredictorTab"
        component={PredictorNavigator}
        options={{ title: "Predictor", tabBarIcon: makeTabBarIcon("PredictorTab") }}
      />
      <MainTab.Screen
        name="ComparisonTab"
        component={ComparisonNavigator}
        options={{ title: "Compare", tabBarIcon: makeTabBarIcon("ComparisonTab") }}
      />
      <MainTab.Screen
        name="SavedTab"
        component={SavedNavigator}
        options={{ title: "Saved", tabBarIcon: makeTabBarIcon("SavedTab") }}
      />
      <MainTab.Screen
        name="AiCounselorTab"
        component={AiCounselorNavigator}
        options={{ title: "AI Counselor", tabBarIcon: makeTabBarIcon("AiCounselorTab") }}
      />
      <MainTab.Screen
        name="ProfileTab"
        component={ProfileNavigator}
        options={{ title: "Profile", tabBarIcon: makeTabBarIcon("ProfileTab") }}
      />
    </MainTab.Navigator>
  );
}

// Wraps the tab bar so CollegeDetail is reachable via navigation.navigate()
// from any nested navigator -- Predictor's own stack, the AI Counselor
// drawer, and later Saved Colleges -- without registering the screen in
// each of their stacks separately. See navigation/types.ts.
function AuthenticatedNavigator() {
  return (
    <AuthenticatedStack.Navigator screenOptions={headerScreenOptions}>
      <AuthenticatedStack.Screen name="Main" component={MainNavigator} options={{ headerShown: false }} />
      <AuthenticatedStack.Screen
        name="CollegeDetail"
        component={CollegeDetailScreen}
        options={{ title: "College Details" }}
      />
    </AuthenticatedStack.Navigator>
  );
}

export function RootNavigator() {
  const status = useAuthStore((state) => state.status);
  const bootstrap = useAuthStore((state) => state.bootstrap);

  useEffect(() => {
    bootstrap();
  }, [bootstrap]);

  if (status === "bootstrapping") {
    return (
      <View style={styles.loading}>
        <ActivityIndicator color={colors.primary} size="large" />
      </View>
    );
  }

  return status === "authenticated" ? <AuthenticatedNavigator /> : <AuthNavigator />;
}

const styles = StyleSheet.create({
  loading: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: colors.background,
  },
});
