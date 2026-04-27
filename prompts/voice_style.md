## Gemini 2.5 Flash TTS — voice direction

"Read this naturally — like you're telling a friend a wild story they've never heard. Conversational warmth, not narration. Put weight on the surprising details. Slight pause where there are commas, brief beats at sentence ends. Don't sound like an audiobook or a news anchor. Sound like a real person."

Voice: **Algieba** (locked in `src/config.py` as `DEFAULT_VOICE`) — smoother and more human than Puck.

Post-processing: ffmpeg `atempo=1.05` is applied (light, just to tighten pacing without going chipmunk).
