// Locked theme constants. Updated v3: cleaner type, amber highlight, modern geometric.
export const theme = {
  color: {
    accent: "#E50914",        // signature red — used sparingly as accent
    accentSoft: "#FFC857",    // amber for caption emphasis (less fatiguing than red)
    bgDark: "#0A0A0A",
    textLight: "#F5F5F5",
    textDim: "#9A9A9A",
    iMessageGray: "#26252A",
    iMessageBlue: "#0A84FF",
  },
  font: {
    // Space Grotesk: hook + cliffhanger (geometric, modern, premium)
    display: "'Space Grotesk', 'Inter', system-ui, sans-serif",
    // Inter: captions + body (highly readable, clean)
    headline: "'Inter', system-ui, sans-serif",
    body: "'Inter', system-ui, sans-serif",
    mono: "'JetBrains Mono', 'SF Mono', Menlo, monospace",
    handwrite: "'Caveat', 'Bradley Hand', cursive",
  },
  // Safe zones (vertical, in % of 1920) — keep critical content inside SAFE
  safe: {
    top: 0.08,     // 0-8% reserved (Shorts progress bar / notch)
    bottom: 0.78,  // anything below 78% likely covered by Shorts UI
  },
  fps: 30,
  size: { width: 1080, height: 1920 },
} as const;
