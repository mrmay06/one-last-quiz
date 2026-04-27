// v3 — clean Hormozi-inspired captions: white Inter Black, amber word emphasis, no red boxes.
// Positioned in safe zone (lower-middle, NOT at the very bottom which YT Shorts UI covers).
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../styles/theme";

export type WordTiming = { word: string; start: number; end: number };

type Props = {
  words: WordTiming[];
  // 0..1 — vertical center of the caption block. Default 0.55 = lower-middle (safe).
  yPercent?: number;
};

const PHRASE_WORDS = 2; // 2 words per phrase
const HIGHLIGHT_EVERY = 4; // every 4th phrase gets amber emphasis

export const KineticCaptions: React.FC<Props> = ({ words, yPercent = 0.55 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (!words || words.length === 0) return null;

  const phrases: { text: string; start: number; end: number; idx: number }[] = [];
  for (let i = 0; i < words.length; i += PHRASE_WORDS) {
    const slice = words.slice(i, i + PHRASE_WORDS);
    phrases.push({
      text: slice.map((w) => w.word).join(" "),
      start: slice[0].start,
      end: slice[slice.length - 1].end,
      idx: phrases.length,
    });
  }

  const sec = frame / fps;
  const active = phrases.find((p) => sec >= p.start && sec <= p.end + 0.06);
  if (!active) return null;

  const localStart = active.start * fps;
  const enter = spring({
    frame: frame - localStart,
    fps,
    config: { damping: 18, stiffness: 220, mass: 0.4 },
  });
  const opacity = interpolate(frame - localStart, [0, 4], [0, 1], { extrapolateRight: "clamp" });
  const isAccent = active.idx % HIGHLIGHT_EVERY === HIGHLIGHT_EVERY - 1;

  return (
    <div
      style={{
        position: "absolute",
        top: `${yPercent * 100}%`,
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        pointerEvents: "none",
        opacity,
        zIndex: 50,
        transform: "translateY(-50%)",
      }}
    >
      <div
        style={{
          padding: "0 60px",
          transform: `scale(${0.92 + enter * 0.08})`,
        }}
      >
        <div
          style={{
            fontFamily: theme.font.headline,
            fontSize: 92,
            color: isAccent ? theme.color.accentSoft : theme.color.textLight,
            fontWeight: 900,
            letterSpacing: -1,
            textAlign: "center",
            lineHeight: 1.05,
            textShadow:
              "0 2px 6px rgba(0,0,0,0.85), 0 6px 30px rgba(0,0,0,0.7)",
            whiteSpace: "nowrap",
            textTransform: "uppercase",
          }}
        >
          {active.text}
        </div>
      </div>
    </div>
  );
};
