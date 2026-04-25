import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../styles/theme";

export const CountdownTimer: React.FC<{
  from: number; // start frame
  durationFrames: number; // total length (will count 5..1)
  startNumber?: number;
}> = ({ from, durationFrames, startNumber = 5 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = frame - from;
  if (local < 0 || local >= durationFrames) return null;

  const perTick = durationFrames / startNumber;
  const tick = Math.min(startNumber - 1, Math.floor(local / perTick));
  const value = startNumber - tick;
  const tickLocal = local - tick * perTick;
  const scale = interpolate(tickLocal, [0, perTick * 0.4, perTick], [1.4, 1.0, 0.9], {
    extrapolateRight: "clamp",
  });
  const opacity = interpolate(tickLocal, [0, perTick * 0.5, perTick * 0.9], [1, 1, 0], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          fontFamily: theme.font.headline,
          fontSize: 540,
          color: theme.color.accent,
          fontWeight: 900,
          transform: `scale(${scale})`,
          opacity,
          textShadow: "0 0 80px rgba(229,9,20,0.55)",
        }}
      >
        {value}
      </div>
    </div>
  );
};
