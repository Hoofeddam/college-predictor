import { request } from "./client";
import { User } from "./types";

interface SignupResponse {
  user: User;
}

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

interface MeResponse {
  user: User;
}

// Returns only { user } -- no tokens. The caller must log in separately
// afterwards (docs/API.md).
export function signup(username: string, email: string, password: string): Promise<SignupResponse> {
  return request<SignupResponse>("/auth/signup", {
    method: "POST",
    body: JSON.stringify({ username, email, password }),
  });
}

export function login(email: string, password: string): Promise<LoginResponse> {
  return request<LoginResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

// Session-validation semantics, distinct from GET /profile (which is the
// Profile screen's own data fetch, even though the two happen to return
// the same shape today).
export function me(): Promise<MeResponse> {
  return request<MeResponse>("/auth/me");
}
