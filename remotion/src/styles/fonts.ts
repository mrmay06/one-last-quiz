// v4 fonts: Space Grotesk (hook + cliffhanger), Inter (captions + body), Caveat (handwriting), JetBrains (mono).
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadSpaceGrotesk } from "@remotion/google-fonts/SpaceGrotesk";
import { loadFont as loadCaveat } from "@remotion/google-fonts/Caveat";
import { loadFont as loadJetBrains } from "@remotion/google-fonts/JetBrainsMono";

loadInter("normal", { weights: ["400", "500", "600", "700", "800", "900"] });
loadSpaceGrotesk("normal", { weights: ["500", "600", "700"] });
loadCaveat("normal", { weights: ["400", "500", "700"] });
loadJetBrains("normal", { weights: ["400", "600"] });
