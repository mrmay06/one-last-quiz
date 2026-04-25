import { Composition, staticFile } from "remotion";
import { AtmosphericPuzzle } from "./templates/AtmosphericPuzzle";
import { FakeIMessage } from "./templates/FakeIMessage";
import { IQTest } from "./templates/IQTest";
import { theme } from "./styles/theme";

const { width, height } = theme.size;
const fps = theme.fps;

export const Root: React.FC = () => {
  return (
    <>
      <Composition
        id="AtmosphericPuzzle"
        component={AtmosphericPuzzle}
        durationInFrames={600} // 20s
        fps={fps}
        width={width}
        height={height}
        defaultProps={{
          imageUrl: staticFile("sample/atmospheric.jpg"),
          hook: "99% fail this riddle.",
          puzzleText:
            "A man pushes his car to a hotel and tells the owner he's bankrupt. Why?",
          answer: "He's playing Monopoly. He landed on the hotel.",
          voiceoverPath: staticFile("sample/voice.wav"),
          bgMusicPath: staticFile("sample/music.mp3"),
        }}
      />
      <Composition
        id="FakeIMessage"
        component={FakeIMessage}
        durationInFrames={660} // 22s
        fps={fps}
        width={width}
        height={height}
        defaultProps={{
          imageUrl: staticFile("sample/atmospheric.jpg"),
          contactName: "Dad",
          messages: [
            { text: "I need to tell you something.", sender: "them" as const, timestamp: "14:30" },
            { text: "There's a body in the basement.", sender: "them" as const, timestamp: "14:31" },
            { text: "Don't tell your mother.", sender: "them" as const, timestamp: "14:31" },
            { text: "wait what", sender: "you" as const, timestamp: "14:32" },
            { text: "It's the freezer. Power cut.", sender: "them" as const, timestamp: "14:32" },
          ],
          answer: "Frozen meat.",
          voiceoverPath: staticFile("sample/voice.wav"),
          bgMusicPath: staticFile("sample/music.mp3"),
          hook: "You won't see this coming.",
        }}
      />
      <Composition
        id="IQTest"
        component={IQTest}
        durationInFrames={540} // 18s
        fps={fps}
        width={width}
        height={height}
        defaultProps={{
          iqData: {
            questionType: "sequence" as const,
            sequence: ["2", "6", "12", "20", "?"],
            options: ["28", "30", "32", "36"],
            correctAnswer: "B" as const,
            explanation: "n² + n: 5²+5 = 30.",
          },
          answer: "B — 30. The pattern is n² + n.",
          voiceoverPath: staticFile("sample/voice.wav"),
          bgMusicPath: staticFile("sample/music.mp3"),
          hook: "Only 3% solve this.",
        }}
      />
    </>
  );
};
