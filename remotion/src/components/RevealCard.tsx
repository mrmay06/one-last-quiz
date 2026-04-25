import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../styles/theme";

export const RevealCard: React.FC<{
  from: number;
  answer: string;
  cta?: string;
}> = ({ from, answer, cta = "Bet you got it wrong." }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = frame - from;
  if (local < 0) return null;

  const enter = spring({
    frame: local,
    fps,
    config: { damping: 12, stiffness: 140, mass: 0.6 },
  });
  const scale = enter;

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        background: "rgba(0,0,0,0.35)",
      }}
    >
      <div
        style={{
          transform: `scale(${scale})`,
          background: theme.color.accent,
          padding: "60px 80px",
          borderRadius: 24,
          maxWidth: "85%",
          boxShadow: "0 30px 80px rgba(229,9,20,0.4)",
        }}
      >
        <div
          style={{
            fontFamily: theme.font.headline,
            fontSize: 72,
            color: theme.color.textLight,
            textTransform: "uppercase",
            letterSpacing: 3,
            marginBottom: 24,
            opacity: 0.85,
          }}
        >
          Answer
        </div>
        <div
          style={{
            fontFamily: theme.font.body,
            fontSize: 64,
            color: theme.color.textLight,
            fontWeight: 700,
            lineHeight: 1.25,
          }}
        >
          {answer}
        </div>
      </div>
      <div
        style={{
          marginTop: 60,
          fontFamily: theme.font.headline,
          fontSize: 64,
          color: theme.color.textLight,
          textTransform: "uppercase",
          letterSpacing: 2,
          opacity: 0.9,
        }}
      >
        {cta}
      </div>
    </div>
  );
};
