import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../styles/theme";

export type Sender = "them" | "you";

export const IMessageBubble: React.FC<{
  text: string;
  sender: Sender;
  appearAtFrame: number;
  showTypingFor?: number; // frames before bubble appears
}> = ({ text, sender, appearAtFrame, showTypingFor = 30 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = frame - appearAtFrame;
  const typingStart = local + showTypingFor;
  const showTyping = typingStart >= 0 && local < 0;
  if (typingStart < 0) return null;

  const isThem = sender === "them";
  const bubbleColor = isThem ? theme.color.iMessageGray : theme.color.iMessageBlue;
  const align = isThem ? "flex-start" : "flex-end";

  if (showTyping) {
    return <TypingBubble align={align} bubbleColor={theme.color.iMessageGray} />;
  }

  const enter = spring({
    frame: local,
    fps,
    config: { damping: 12, stiffness: 180, mass: 0.5 },
  });
  const scale = 0.85 + 0.15 * enter;
  const opacity = interpolate(local, [0, 8], [0, 1], { extrapolateRight: "clamp" });

  return (
    <div
      style={{
        display: "flex",
        justifyContent: align,
        padding: "12px 32px",
        opacity,
        transform: `scale(${scale})`,
        transformOrigin: isThem ? "left center" : "right center",
      }}
    >
      <div
        style={{
          maxWidth: "78%",
          background: bubbleColor,
          color: theme.color.textLight,
          padding: "26px 36px",
          borderRadius: 44,
          fontFamily: theme.font.body,
          fontSize: 44,
          lineHeight: 1.3,
          fontWeight: 500,
        }}
      >
        {text}
      </div>
    </div>
  );
};

const TypingBubble: React.FC<{ align: "flex-start" | "flex-end"; bubbleColor: string }> = ({
  align,
  bubbleColor,
}) => {
  const frame = useCurrentFrame();
  const dots = [0, 1, 2].map((i) => {
    const phase = (frame - i * 5) % 30;
    const opacity = phase < 15 ? 0.4 + (phase / 15) * 0.6 : 0.4 + ((30 - phase) / 15) * 0.6;
    return opacity;
  });
  return (
    <div style={{ display: "flex", justifyContent: align, padding: "12px 32px" }}>
      <div
        style={{
          background: bubbleColor,
          padding: "20px 32px",
          borderRadius: 44,
          display: "flex",
          gap: 10,
        }}
      >
        {dots.map((o, i) => (
          <div
            key={i}
            style={{
              width: 16,
              height: 16,
              borderRadius: "50%",
              background: "#9A9A9A",
              opacity: o,
            }}
          />
        ))}
      </div>
    </div>
  );
};
