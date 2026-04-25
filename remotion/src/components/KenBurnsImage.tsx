import { Img, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

export const KenBurnsImage: React.FC<{
  src: string;
  fromScale?: number;
  toScale?: number;
}> = ({ src, fromScale = 1.0, toScale = 1.08 }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const scale = interpolate(frame, [0, durationInFrames], [fromScale, toScale], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        overflow: "hidden",
        backgroundColor: "#000",
      }}
    >
      <Img
        src={src}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${scale})`,
          transformOrigin: "center",
        }}
      />
      {/* Vignette + dark overlay for legibility */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(ellipse at center, rgba(0,0,0,0.2) 30%, rgba(0,0,0,0.75) 100%)",
        }}
      />
    </div>
  );
};
