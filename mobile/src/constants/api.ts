// 127.0.0.1 works for Expo web (same machine as the Flask dev server). A
// physical device or emulator needs the machine's LAN IP instead -- see
// .env.example.
export const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? "http://127.0.0.1:5000";

export const API_PREFIX = "/api/v1";
