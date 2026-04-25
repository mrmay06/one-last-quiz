import { AbsoluteFill, Audio, Img, Sequence, interpolate, useCurrentFrame } from "remotion";
import { IMessageBubble, type Sender } from "../components/IMessageBubble";
import { theme } from "../styles/theme";

export type Message = { text: string; sender: Sender; timestamp: string };

export type IMessageProps = {
  imageUrl: string;
  contactName: string;
  messages: Message[];
  answer: string;
  hook: string;
  voiceoverPath: string;
  bgMusicPath: string;
};

export const FakeIMessage: React.FC<IMessageProps> = ({
  imageUrl,
  contactName,
  messages,
  answer,
  hook,
  voiceoverPath,
  bgMusicPath,
}) => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{ background: theme.color.bgDark }}>
      {/* Blurred background */}
      <Img
        src={imageUrl}
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          objectFit: "cover",
          filter: "blur(28px) brightness(0.4)",
          transform: "scale(1.15)",
        }}
      />

      {/* iMessage chrome */}
      <ChatHeader name={contactName} />

      {/* Messages — start appearing from frame 120 (4s) */}
      <div
        style={{
          position: "absolute",
          top: 280,
          bottom: 200,
          left: 0,
          right: 0,
          display: "flex",
          flexDirection: "column",
          justifyContent: "flex-end",
          paddingBottom: 40,
        }}
      >
        {messages.map((m, i) => (
          <IMessageBubble
            key={i}
            text={m.text}
            sender={m.sender}
            appearAtFrame={120 + i * 75}
            showTypingFor={30}
          />
        ))}
        {/* Reveal bubble at the end */}
        <Sequence from={600}>
          <IMessageBubble text={answer} sender="you" appearAtFrame={0} showTypingFor={20} />
        </Sequence>
      </div>

      {/* Hook overlay banner — fades out after 2s */}
      {frame < 80 && <NotificationBanner contact={contactName} text={hook} />}

      <Audio src={voiceoverPath} />
      <Audio src={bgMusicPath} volume={0.15} />
    </AbsoluteFill>
  );
};

const ChatHeader: React.FC<{ name: string }> = ({ name }) => (
  <div
    style={{
      position: "absolute",
      top: 0,
      left: 0,
      right: 0,
      paddingTop: 80,
      paddingBottom: 24,
      background: "rgba(20,20,22,0.92)",
      backdropFilter: "blur(20px)",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      borderBottom: "1px solid rgba(255,255,255,0.08)",
    }}
  >
    <div
      style={{
        width: 120,
        height: 120,
        borderRadius: "50%",
        background: "linear-gradient(135deg, #555, #222)",
        marginBottom: 12,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: theme.font.body,
        fontSize: 56,
        color: theme.color.textLight,
        fontWeight: 700,
      }}
    >
      {name.slice(0, 1)}
    </div>
    <div
      style={{
        fontFamily: theme.font.body,
        fontSize: 38,
        color: theme.color.textLight,
        fontWeight: 600,
      }}
    >
      {name}
    </div>
  </div>
);

const NotificationBanner: React.FC<{ contact: string; text: string }> = ({ contact, text }) => {
  const frame = useCurrentFrame();
  const y = interpolate(frame, [0, 18, 60, 80], [-200, 40, 40, -200], {
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 40,
        right: 40,
        transform: `translateY(${y}px)`,
        background: "rgba(50,50,55,0.95)",
        borderRadius: 24,
        padding: "28px 36px",
        backdropFilter: "blur(20px)",
        boxShadow: "0 12px 40px rgba(0,0,0,0.5)",
      }}
    >
      <div
        style={{
          fontFamily: theme.font.body,
          fontSize: 32,
          color: theme.color.textLight,
          fontWeight: 700,
          marginBottom: 8,
        }}
      >
        {contact}
      </div>
      <div
        style={{
          fontFamily: theme.font.body,
          fontSize: 30,
          color: theme.color.textLight,
          fontWeight: 400,
          opacity: 0.85,
        }}
      >
        {text}
      </div>
    </div>
  );
};
