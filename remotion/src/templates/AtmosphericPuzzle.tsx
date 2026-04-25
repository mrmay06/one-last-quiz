import { AbsoluteFill, Audio, Sequence, interpolate, useCurrentFrame } from "remotion";
import { CountdownTimer } from "../components/CountdownTimer";
import { HookOverlay } from "../components/HookOverlay";
import { KenBurnsImage } from "../components/KenBurnsImage";
import { RevealCard } from "../components/RevealCard";
import { theme } from "../styles/theme";

export type AtmosphericProps = {
  imageUrl: string;
  hook: string;
  puzzleText: string;
  answer: string;
  voiceoverPath: string;
  bgMusicPath: string;
};

export const AtmosphericPuzzle: React.FC<AtmosphericProps> = ({
  imageUrl,
  hook,
  puzzleText,
  answer,
  voiceoverPath,
  bgMusicPath,
}) => {
  return (
    <AbsoluteFill style={{ background: theme.color.bgDark }}>
      <KenBurnsImage src={imageUrl} />

      {/* Hook 0–2s */}
      <Sequence from={0} durationInFrames={60}>
        <HookOverlay text={hook} from={0} to={60} />
      </Sequence>

      {/* Puzzle text 2–12s */}
      <Sequence from={60} durationInFrames={300}>
        <PuzzleTextBlock text={puzzleText} />
      </Sequence>

      {/* Countdown 12–15s */}
      <Sequence from={360} durationInFrames={90}>
        <CountdownTimer from={0} durationFrames={90} startNumber={3} />
      </Sequence>

      {/* Reveal 15–20s */}
      <Sequence from={450} durationInFrames={150}>
        <RevealCard from={0} answer={answer} />
      </Sequence>

      <Audio src={voiceoverPath} />
      <Audio src={bgMusicPath} volume={0.18} />
    </AbsoluteFill>
  );
};

const PuzzleTextBlock: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });
  const y = interpolate(frame, [0, 30], [40, 0], { extrapolateRight: "clamp" });
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "0 80px",
        opacity,
        transform: `translateY(${y}px)`,
      }}
    >
      <div
        style={{
          fontFamily: theme.font.body,
          fontSize: 68,
          color: theme.color.textLight,
          textAlign: "center",
          fontWeight: 600,
          lineHeight: 1.35,
          textShadow: "0 4px 24px rgba(0,0,0,0.85)",
        }}
      >
        {text}
      </div>
    </div>
  );
};
