import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../styles/theme";

export const HookOverlay: React.FC<{ text: string; from?: number; to?: number }> = ({
  text,
  from = 0,
  to = 60,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = frame - from;
  const opacity = interpolate(local, [0, 15, to - from - 15, to - from], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const scale = spring({ frame: local, fps, config: { damping: 200, stiffness: 120 } });
  return (
    <div
      style={{
        position: "absolute",
        top: "18%",
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        opacity,
      }}
    >
      <div
        style={{
          padding: "24px 48px",
          background: "rgba(0,0,0,0.55)",
          border: `4px solid ${theme.color.accent}`,
          borderRadius: 16,
          transform: `scale(${0.85 + scale * 0.15})`,
        }}
      >
        <div
          style={{
            fontFamily: theme.font.headline,
            fontSize: 96,
            color: theme.color.textLight,
            textTransform: "uppercase",
            letterSpacing: 2,
            textAlign: "center",
            lineHeight: 1.05,
          }}
        >
          {text}
        </div>
      </div>
    </div>
  );
};
