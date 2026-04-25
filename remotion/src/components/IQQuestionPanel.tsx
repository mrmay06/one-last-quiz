import { theme } from "../styles/theme";

type SequenceData = {
  questionType: "sequence";
  sequence: string[];
  options: string[];
  correctAnswer: "A" | "B" | "C" | "D";
  explanation: string;
};

type Shape = {
  id: "A" | "B" | "C" | "D";
  type: "triangle" | "circle" | "square" | "diamond";
  rotation: number;
  filled: boolean;
};

type OddOneOutData = {
  questionType: "oddOneOut";
  shapes: Shape[];
  correctAnswer: "A" | "B" | "C" | "D";
  explanation: string;
};

export type IQData = SequenceData | OddOneOutData;

export const IQQuestionPanel: React.FC<{
  data: IQData;
  highlight?: "A" | "B" | "C" | "D" | null;
}> = ({ data, highlight }) => {
  if (data.questionType === "sequence") {
    return <SequencePanel data={data} highlight={highlight} />;
  }
  return <OddOneOutPanel data={data} highlight={highlight} />;
};

const labelOf = (i: number) => (["A", "B", "C", "D"] as const)[i];

const Cell: React.FC<{
  label: "A" | "B" | "C" | "D";
  highlight: boolean;
  children: React.ReactNode;
}> = ({ label, highlight, children }) => (
  <div
    style={{
      flex: 1,
      aspectRatio: "1 / 1",
      border: `4px solid ${highlight ? theme.color.accent : "#2A2A2A"}`,
      borderRadius: 24,
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      background: highlight ? "rgba(229,9,20,0.18)" : "rgba(255,255,255,0.03)",
      boxShadow: highlight ? `0 0 60px ${theme.color.accent}` : undefined,
      position: "relative",
    }}
  >
    <div
      style={{
        position: "absolute",
        top: 16,
        left: 24,
        fontFamily: theme.font.mono,
        fontSize: 38,
        color: highlight ? theme.color.accent : theme.color.textDim,
        fontWeight: 700,
      }}
    >
      {label}
    </div>
    {children}
  </div>
);

const SequencePanel: React.FC<{ data: SequenceData; highlight?: "A" | "B" | "C" | "D" | null }> = ({
  data,
  highlight,
}) => {
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        padding: "120px 80px",
        display: "flex",
        flexDirection: "column",
        gap: 80,
      }}
    >
      <div
        style={{
          fontFamily: theme.font.headline,
          fontSize: 96,
          color: theme.color.textLight,
          textAlign: "center",
          letterSpacing: 6,
          lineHeight: 1.1,
        }}
      >
        {data.sequence.join("  ,  ")}
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 32, flex: 1 }}>
        {data.options.map((opt, i) => {
          const label = labelOf(i);
          return (
            <Cell key={label} label={label} highlight={highlight === label}>
              <div
                style={{
                  fontFamily: theme.font.headline,
                  fontSize: 160,
                  color: theme.color.textLight,
                  fontWeight: 800,
                }}
              >
                {opt}
              </div>
            </Cell>
          );
        })}
      </div>
    </div>
  );
};

const OddOneOutPanel: React.FC<{
  data: OddOneOutData;
  highlight?: "A" | "B" | "C" | "D" | null;
}> = ({ data, highlight }) => {
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        padding: "200px 80px",
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        gap: 32,
      }}
    >
      {data.shapes.map((s) => (
        <Cell key={s.id} label={s.id} highlight={highlight === s.id}>
          <ShapeSvg shape={s} />
        </Cell>
      ))}
    </div>
  );
};

const ShapeSvg: React.FC<{ shape: Shape }> = ({ shape }) => {
  const fill = shape.filled ? theme.color.textLight : "none";
  const stroke = theme.color.textLight;
  const props = { fill, stroke, strokeWidth: 8 };
  let geom: React.ReactNode;
  switch (shape.type) {
    case "triangle":
      geom = <polygon points="100,20 180,170 20,170" {...props} />;
      break;
    case "circle":
      geom = <circle cx="100" cy="100" r="80" {...props} />;
      break;
    case "square":
      geom = <rect x="20" y="20" width="160" height="160" {...props} />;
      break;
    case "diamond":
      geom = <polygon points="100,15 185,100 100,185 15,100" {...props} />;
      break;
  }
  return (
    <svg
      width="240"
      height="240"
      viewBox="0 0 200 200"
      style={{ transform: `rotate(${shape.rotation}deg)` }}
    >
      {geom}
    </svg>
  );
};
