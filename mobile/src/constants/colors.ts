// Ported from the web app's design tokens (static/css/main.css, light mode
// only — mobile dark mode isn't in scope yet). Only the tokens Phase 1's
// screens actually use; add more as later phases need them.

export const colors = {
  background: "#F1F2F4",
  surface: "#FFFFFF",
  text: "#16202C",
  textMuted: "#4B5A68",
  textFaint: "#7C8996",
  border: "#D7DBE1",
  borderStrong: "#B9C0C9",
  primary: "#15395C",
  primaryStrong: "#0E2740",
  danger: "#9B3D3D",
  dangerTint: "#F3E4E4",
  success: "#3D7A5A",
  successTint: "#E3F0E9",
  brass: "#93711F",
  brassTint: "#F1E7D2",
  // Android ripple overlays for Pressable's android_ripple prop -- not UI
  // "content" colors, but centralized here for the same reason every other
  // color is: nothing hardcoded outside this file.
  rippleOnLight: "rgba(15, 25, 35, 0.08)",
  rippleOnDark: "rgba(255, 255, 255, 0.2)",
};
