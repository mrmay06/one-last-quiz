import { Composition } from "remotion";
import { AtmosphericPuzzle } from "./templates/AtmosphericPuzzle";
import { theme } from "./styles/theme";
import "./styles/fonts";

const { width, height } = theme.size;
const fps = theme.fps;
const FALLBACK_FRAMES = 540;

export const Root: React.FC = () => {
  return (
    <Composition
      id="AtmosphericPuzzle"
      component={AtmosphericPuzzle}
      durationInFrames={FALLBACK_FRAMES}
      fps={fps}
      width={width}
      height={height}
      calculateMetadata={({ props }) => ({
        durationInFrames: (props as any).totalFrames ?? FALLBACK_FRAMES,
      })}
      defaultProps={{
        hook: "99% fail this.",
        cta: "Drop your guess.",
        imageCuts: [],
        voiceoverPath: "",
        bgMusicPath: "",
        captions: [],
        cliffhangerStartFrame: 480,
        hookDurationFrames: 90,
      }}
    />
  );
};
