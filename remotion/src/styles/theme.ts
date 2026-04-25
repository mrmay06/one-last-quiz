// Locked theme constants — do not change without updating PRD §5.
export const theme = {
  color: {
    accent: "#E50914",
    bgDark: "#0A0A0A",
    textLight: "#F5F5F5",
    textDim: "#9A9A9A",
    iMessageGray: "#26252A",
    iMessageBlue: "#0A84FF",
  },
  font: {
    headline: "Anton, Impact, sans-serif",
    body: "Inter, system-ui, sans-serif",
    mono: "'SF Mono', Menlo, monospace",
  },
  fps: 30,
  size: { width: 1080, height: 1920 },
} as const;
