import { request } from "./client";
import { User } from "./types";

interface ProfileResponse {
  user: User;
}

export function getProfile(): Promise<ProfileResponse> {
  return request<ProfileResponse>("/profile");
}
