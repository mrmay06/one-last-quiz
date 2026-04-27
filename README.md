# One Last Quiz V2

Atmospheric-only YouTube Shorts pipeline for riddle videos. Each run picks a curated riddle, rewrites it into short-form copy, generates a timed image plan, creates narration, aligns captions, renders a vertical MP4 in Remotion, and uploads it.

**Stack:** Python 3.11 · GPT-4o · Gemini TTS · Pollinations · Remotion v4 · GitHub Actions

## Product Scope

V2 is intentionally narrow:
- one active template: `atmospheric`
- one script path: riddle bank -> GPT rewrite -> 3-4 image prompts
- one renderer: `AtmosphericPuzzle`
- one primary publisher: YouTube Shorts
- optional secondary publisher: Facebook Reels

The riddle bank is the source of puzzle logic. GPT does not invent riddles; it packages them for Shorts and creates the image plan.

## Runtime Flow

```text
cron / manual run
  -> src/orchestrator.py
  -> src/riddle_bank.py        pick unused atmospheric riddle
  -> src/script_gen.py         GPT-4o rewrite + image_prompts[]
  -> src/image_gen.py          Pollinations image generation
  -> src/voice_gen.py          Gemini TTS voiceover
  -> src/captions.py           word-level alignment
  -> src/music_picker.py       random local music bed
  -> src/video_render.py       Remotion render
  -> src/thumbnail.py          hook-based thumbnail
  -> src/upload_youtube.py     upload + thumbnail + answer comment
  -> data/used_puzzles.json    log usage
```

## Project Structure

```text
src/                     Python pipeline
remotion/                Remotion render project
prompts/                 Locked prompt assets for script + voice + image style
assets/music/            Local royalty-free music library
data/                    Riddle bank, usage log, and error log
scripts/                 One-off helpers
.github/workflows/       Scheduled automation
```

## Required Secrets

Add these to your local `.env` and to GitHub Actions secrets:

| Secret | Required | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | yes | script generation |
| `GEMINI_API_KEY` | yes | TTS generation |
| `POLLINATIONS_API_KEY` | optional | authenticated image requests |
| `YOUTUBE_CLIENT_ID` | yes | YouTube upload OAuth |
| `YOUTUBE_CLIENT_SECRET` | yes | YouTube upload OAuth |
| `YOUTUBE_REFRESH_TOKEN` | yes | YouTube upload OAuth |
| `FACEBOOK_ENABLED` | optional | enable Facebook publishing |
| `FACEBOOK_PAGE_ID` | optional | Facebook Reels |
| `FACEBOOK_PAGE_ACCESS_TOKEN` | optional | Facebook Reels |

## Local Setup

```bash
git clone https://github.com/mrmay06/one-last-quiz.git
cd one-last-quiz
pip install -r requirements.txt
cd remotion && npm install && cd ..
```

Add MP3 music files to `assets/music/`.

To generate a YouTube refresh token:

```bash
python scripts/get_refresh_token.py
```

## Local Commands

```bash
python -m src.script_gen
python -m src.orchestrator --skip-upload
cd remotion && npm run studio
cd remotion && npm run lint
```

## What Changed In V2

V2 removes the dormant multi-template surface from the shipped path. The codebase now reflects the actual product instead of carrying inactive `found_format` and `iq` branches through docs, config, and rendering.

## Notes

- Generated Remotion assets are written to `remotion/public/run/` at runtime.
- Final video is written to `tmp/output.mp4`.
- `data/used_puzzles.json` is committed back by the GitHub Action to avoid repeats.
- The YouTube answer comment is posted automatically, but true pinning still has to be done manually in YouTube Studio.
