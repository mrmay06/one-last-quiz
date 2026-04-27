// Programmatic Remotion render — gives us full control over bundle + public dir.
// Usage: node render.mjs <CompositionId> <outputPath> '<json props>'
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const [, , compositionId, outputLocation, propsJson] = process.argv;
if (!compositionId || !outputLocation) {
  console.error("Usage: node render.mjs <CompositionId> <outputPath> '<json props>'");
  process.exit(1);
}

const inputProps = propsJson ? JSON.parse(propsJson) : {};

const bundleLocation = await bundle({
  entryPoint: path.join(__dirname, "src", "index.ts"),
  publicDir: path.join(__dirname, "public"),
});

console.log("Bundle ready at:", bundleLocation);

const composition = await selectComposition({
  serveUrl: bundleLocation,
  id: compositionId,
  inputProps,
});

await renderMedia({
  composition,
  serveUrl: bundleLocation,
  codec: "h264",
  outputLocation,
  inputProps,
  concurrency: 1,
  onProgress: ({ progress }) => {
    if (Math.round(progress * 100) % 10 === 0) {
      process.stdout.write(`Render progress: ${Math.round(progress * 100)}%\r`);
    }
  },
});

console.log(`\nRendered: ${outputLocation}`);
