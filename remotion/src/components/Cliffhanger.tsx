// v4 — minimal cliffhanger. Hard cut to black + single line + arrow. Holds ~1.5s.
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../styles/theme";

export const Cliffhanger: React.FC<{
  cta: string;
  startFrame: number;
}> = ({ cta, startFrame }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = frame - startFrame;
  if (local < 0) return null;

  // Hard cut to black — instant
  const enter = spring({
    frame: local,
    fps,
    config: { damping: 18, stiffness: 200, mass: 0.5 },
  });
  const textOpacity = interpolate(local, [2, 12], [0, 1], { extrapolateRight: "clamp" });
  const scale = 0.94 + 0.06 * enter;

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        background: "#000",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "0 60px",
        zIndex: 60,
      }}
    >
      <div
        style={{
          fontFamily: theme.font.display,
          fontSize: 96,
          color: theme.color.textLight,
          letterSpacing: -1.5,
          textAlign: "center",
          lineHeight: 1.1,
          fontWeight: 700,
          opacity: textOpacity,
          transform: `scale(${scale})`,
        }}
      >
        {cta}
      </div>
    </div>
  );
};
