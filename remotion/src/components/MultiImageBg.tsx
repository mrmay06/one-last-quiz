// v3 — stronger Ken Burns: scale 1.0 → 1.20 + directional pan per segment.
// Each cut alternates pan direction so motion feels intentional, not random.
import { AbsoluteFill, Img, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

export type ImageCut = { src: string; cutAtFrame: number };

const FADE_FRAMES = 14;
const MAX_SCALE = 1.2;
const PAN_PX = 60;

export const MultiImageBg: React.FC<{ cuts: ImageCut[] }> = ({ cuts }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  if (!cuts || cuts.length === 0) return null;

  const segments = cuts.map((c, i) => ({
    src: c.src,
    start: c.cutAtFrame,
    end: i + 1 < cuts.length ? cuts[i + 1].cutAtFrame : durationInFrames,
  }));

  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {segments.map((seg, i) => {
        const opacity = interpolate(
          frame,
          [seg.start - FADE_FRAMES, seg.start, seg.end - FADE_FRAMES, seg.end],
          [0, 1, 1, i + 1 < segments.length ? 0 : 1],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
        );
        if (opacity <= 0) return null;

        const segFrame = frame - seg.start;
        const segLen = Math.max(seg.end - seg.start, 1);
        const t = Math.min(1, Math.max(0, segFrame / segLen));
        const scale = 1.0 + (MAX_SCALE - 1.0) * t;
        // Alternate pan: even = left→right, odd = right→left (slight)
        const direction = i % 2 === 0 ? 1 : -1;
        const tx = PAN_PX * direction * t;
        const ty = (i % 2 === 0 ? -1 : 1) * 30 * t;

        return (
          <div
            key={i}
            style={{
              position: "absolute",
              inset: 0,
              opacity,
              overflow: "hidden",
            }}
          >
            <Img
              src={seg.src}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                transform: `scale(${scale}) translate(${tx}px, ${ty}px)`,
              }}
            />
          </div>
        );
      })}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(ellipse at center, rgba(0,0,0,0.1) 30%, rgba(0,0,0,0.7) 100%)",
        }}
      />
    </AbsoluteFill>
  );
};
