import { Platform } from "react-native";
import * as SecureStore from "expo-secure-store";

import { ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY } from "../constants/storage";

// expo-secure-store ships a hard stub on web (no keychain equivalent
// exists there) -- calling it throws. This app's real targets are
// iOS/Android, where SecureStore is used unconditionally below. The
// localStorage branch exists only so the app is runnable via
// `expo start --web`, which is how this project is tested in an
// environment without a device simulator. It is not a claim that web
// storage here is secure.
const isWeb = Platform.OS === "web";

function getItem(key: string): Promise<string | null> {
  return isWeb ? Promise.resolve(localStorage.getItem(key)) : SecureStore.getItemAsync(key);
}

async function setItem(key: string, value: string): Promise<void> {
  if (isWeb) {
    localStorage.setItem(key, value);
    return;
  }
  await SecureStore.setItemAsync(key, value);
}

async function deleteItem(key: string): Promise<void> {
  if (isWeb) {
    localStorage.removeItem(key);
    return;
  }
  await SecureStore.deleteItemAsync(key);
}

export function getAccessToken(): Promise<string | null> {
  return getItem(ACCESS_TOKEN_KEY);
}

// No getRefreshToken() yet -- nothing reads the refresh token in Phase 1
// (no auto-refresh, see api/client.ts). It's still stored, ready for when
// that's added. Add the getter then, not before.
export async function setTokens(accessToken: string, refreshToken: string): Promise<void> {
  await setItem(ACCESS_TOKEN_KEY, accessToken);
  await setItem(REFRESH_TOKEN_KEY, refreshToken);
}

export async function clearTokens(): Promise<void> {
  await deleteItem(ACCESS_TOKEN_KEY);
  await deleteItem(REFRESH_TOKEN_KEY);
}
