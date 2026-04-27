// v6 hook overlay — Space Grotesk, sits on subtle dark gradient over the image.
// No box, no rotation. Fades out cleanly after ~2.5s.
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../styles/theme";

export const HookBanner: React.FC<{
  text: string;
  durationFrames: number;
}> = ({ text, durationFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = spring({ frame, fps, config: { damping: 18, stiffness: 200, mass: 0.5 } });
  const scale = 0.96 + 0.04 * enter;
  const fadeIn = interpolate(frame, [0, 6], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [durationFrames - 12, durationFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const opacity = Math.min(fadeIn, fadeOut);
  if (frame >= durationFrames) return null;

  return (
    <>
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: "44%",
          background:
            "linear-gradient(180deg, rgba(0,0,0,0.78) 0%, rgba(0,0,0,0.45) 55%, rgba(0,0,0,0) 100%)",
          opacity,
          zIndex: 39,
          pointerEvents: "none",
        }}
      />
      <div
        style={{
          position: "absolute",
          top: "14%",
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "center",
          opacity,
          zIndex: 40,
          padding: "0 70px",
        }}
      >
        <div style={{ transform: `scale(${scale})`, maxWidth: "100%", textAlign: "center" }}>
          <div
            style={{
              fontFamily: theme.font.display,
              fontSize: 116,
              color: theme.color.textLight,
              letterSpacing: -3,
              lineHeight: 0.98,
              fontWeight: 700,
              textShadow:
                "0 4px 14px rgba(0,0,0,0.9), 0 14px 50px rgba(0,0,0,0.65)",
            }}
          >
            {text}
          </div>
          <div
            style={{
              width: 120,
              height: 6,
              background: theme.color.accent,
              margin: "30px auto 0",
              borderRadius: 3,
            }}
          />
        </div>
      </div>
    </>
  );
};
