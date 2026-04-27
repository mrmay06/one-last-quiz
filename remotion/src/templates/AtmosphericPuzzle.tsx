import { AbsoluteFill, Audio, interpolate, useVideoConfig } from "remotion";
import { Cliffhanger } from "../components/Cliffhanger";
import { HookBanner } from "../components/HookBanner";
import { KineticCaptions, type WordTiming } from "../components/KineticCaptions";
import { MultiImageBg, type ImageCut } from "../components/MultiImageBg";
import { theme } from "../styles/theme";

export type AtmosphericProps = {
  hook: string;
  cta: string;
  imageCuts: ImageCut[];
  voiceoverPath: string;
  bgMusicPath: string;
  captions: WordTiming[];
  cliffhangerStartFrame: number;
  hookDurationFrames: number;
};

const MUSIC_BASE = 0.14;
const MUSIC_FADE_FRAMES = 45;

export const AtmosphericPuzzle: React.FC<AtmosphericProps> = ({
  hook,
  cta,
  imageCuts,
  voiceoverPath,
  bgMusicPath,
  captions,
  cliffhangerStartFrame,
  hookDurationFrames,
}) => {
  const { durationInFrames } = useVideoConfig();
  const fadeStart = durationInFrames - MUSIC_FADE_FRAMES;
  const musicVolume = (frame: number) =>
    interpolate(frame, [fadeStart, durationInFrames], [MUSIC_BASE, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

  return (
    <AbsoluteFill style={{ background: theme.color.bgDark }}>
      {/* Image is visible from frame 0 — no black slate */}
      <MultiImageBg cuts={imageCuts} />
      {/* Hook overlays the image (clean typography on subtle gradient) */}
      <HookBanner text={hook} durationFrames={hookDurationFrames} />
      <KineticCaptions words={captions} yPercent={0.55} />
      <Cliffhanger cta={cta} startFrame={cliffhangerStartFrame} />

      <Audio src={voiceoverPath} />
      <Audio src={bgMusicPath} volume={musicVolume} />
    </AbsoluteFill>
  );
};
