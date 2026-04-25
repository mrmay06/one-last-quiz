import { AbsoluteFill, Audio, Sequence, interpolate, useCurrentFrame } from "remotion";
import { CountdownTimer } from "../components/CountdownTimer";
import { HookOverlay } from "../components/HookOverlay";
import { IQQuestionPanel, type IQData } from "../components/IQQuestionPanel";
import { RevealCard } from "../components/RevealCard";
import { theme } from "../styles/theme";

export type IQProps = {
  iqData: IQData;
  answer: string;
  hook: string;
  voiceoverPath: string;
  bgMusicPath: string;
};

export const IQTest: React.FC<IQProps> = ({
  iqData,
  answer,
  hook,
  voiceoverPath,
  bgMusicPath,
}) => {
  return (
    <AbsoluteFill style={{ background: theme.color.bgDark }}>
      <ParticleBg />

      {/* Hook 0–2s */}
      <Sequence from={0} durationInFrames={60}>
        <HookOverlay text={hook} from={0} to={60} />
      </Sequence>

      {/* Question 2–14s (no highlight) */}
      <Sequence from={60} durationInFrames={360}>
        <IQQuestionPanel data={iqData} highlight={null} />
      </Sequence>

      {/* Depleting timer bar 6s–14s */}
      <Sequence from={180} durationInFrames={240}>
        <DepletingBar />
      </Sequence>

      {/* Countdown 14–16s */}
      <Sequence from={420} durationInFrames={60}>
        <CountdownTimer from={0} durationFrames={60} startNumber={3} />
      </Sequence>

      {/* Reveal 16–18s */}
      <Sequence from={480} durationInFrames={60}>
        <IQQuestionPanel data={iqData} highlight={iqData.correctAnswer} />
        <RevealCard from={0} answer={answer} cta="Bet you got it wrong." />
      </Sequence>

      <Audio src={voiceoverPath} />
      <Audio src={bgMusicPath} volume={0.18} />
    </AbsoluteFill>
  );
};

const ParticleBg: React.FC = () => (
  <div
    style={{
      position: "absolute",
      inset: 0,
      background:
        "radial-gradient(ellipse at top, #1a1a1a 0%, #0a0a0a 60%), radial-gradient(circle at 30% 80%, rgba(229,9,20,0.08), transparent 50%)",
    }}
  />
);

const DepletingBar: React.FC = () => {
  const frame = useCurrentFrame();
  const width = interpolate(frame, [0, 240], [100, 0], { extrapolateRight: "clamp" });
  return (
    <div
      style={{
        position: "absolute",
        top: 60,
        left: 80,
        right: 80,
        height: 12,
        background: "rgba(255,255,255,0.08)",
        borderRadius: 6,
        overflow: "hidden",
      }}
    >
      <div
        style={{
          width: `${width}%`,
          height: "100%",
          background: theme.color.accent,
          transition: "none",
        }}
      />
    </div>
  );
};
