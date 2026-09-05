import { create } from "zustand";

import { me } from "../api/auth";
import { clearSavedCollegesCache } from "../api/saved";
import { User } from "../api/types";
import { clearTokens, getAccessToken, setTokens } from "../storage/tokenStorage";

type AuthStatus = "bootstrapping" | "authenticated" | "unauthenticated";

interface AuthState {
  status: AuthStatus;
  user: User | null;
  login: (accessToken: string, refreshToken: string, user: User) => Promise<void>;
  logout: () => Promise<void>;
  // Runs once on app start: checks for a stored access token and
  // validates it against the backend. No refresh attempt on failure --
  // an invalid/expired token just logs the user out (see api/client.ts).
  bootstrap: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  status: "bootstrapping",
  user: null,

  login: async (accessToken, refreshToken, user) => {
    await setTokens(accessToken, refreshToken);
    set({ status: "authenticated", user });
  },

  logout: async () => {
    await clearTokens();
    clearSavedCollegesCache();
    set({ status: "unauthenticated", user: null });
  },

  bootstrap: async () => {
    const accessToken = await getAccessToken();

    if (!accessToken) {
      set({ status: "unauthenticated", user: null });
      return;
    }

    try {
      const { user } = await me();
      set({ status: "authenticated", user });
    } catch {
      await clearTokens();
      set({ status: "unauthenticated", user: null });
    }
  },
}));
