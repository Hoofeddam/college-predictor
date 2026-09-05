import { API_BASE_URL, API_PREFIX } from "../constants/api";
import { getAccessToken } from "../storage/tokenStorage";
import { ApiError } from "./types";

// Deliberately no refresh-on-401 retry here yet -- Phase 1 proves the auth
// flow with the least networking complexity that works. Auto-refresh,
// request replay and concurrent-refresh handling are a later addition,
// not solved speculatively now.
export async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  let response: Response;

  try {
    const accessToken = await getAccessToken();

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string> | undefined),
    };

    if (accessToken) {
      headers.Authorization = `Bearer ${accessToken}`;
    }

    response = await fetch(`${API_BASE_URL}${API_PREFIX}${path}`, {
      ...options,
      headers,
    });
  } catch {
    throw new ApiError("network_error", "Could not reach the server. Check your connection.", 0);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  let body: unknown = null;

  try {
    body = await response.json();
  } catch {
    body = null;
  }

  if (!response.ok) {
    const errorBody = body as { error?: { code?: string; message?: string } } | null;
    const code = errorBody?.error?.code ?? "unknown_error";
    const message = errorBody?.error?.message ?? "Something went wrong. Please try again.";

    throw new ApiError(code, message, response.status);
  }

  return body as T;
}
