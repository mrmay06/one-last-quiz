# One Last Quiz

Fully automated YouTube Shorts (+ optional Facebook Reels) channel. Publishes 2 ego-bait riddle videos per day with zero human intervention.

**Stack:** Python 3.11 · Gemini 2.5 Flash · Pollinations · Remotion v4 · GitHub Actions

---

## How it works

```
cron (2× daily)
   │
   ▼
orchestrator.py
   │
   ├── pick template   (atmospheric → imessage → iq → repeat)
   ├── script_gen      (Gemini 2.5 Flash → puzzle JSON)
   ├── image_gen       (Pollinations Flux → 1 image; Gemini fallback)
   ├── voice_gen       (Gemini TTS Charon → narration)
   ├── music_picker    (random from assets/music/)
   ├── video_render    (Remotion → 1080×1920 MP4)
   ├── publishers      (YouTube + optional Facebook)
   └── puzzle_store    (log hash + commit back to repo)
```

The **puzzle JSON is the single source of truth** — every downstream module reads from it. Want a different channel concept? Swap `prompts/script_system.md` and the Remotion templates; the pipeline is content-agnostic.

---

## Project structure

```
src/                     Python pipeline (one file per stage)
remotion/                Remotion video project (3 templates, 6 components)
prompts/                 Locked prompts for Gemini
assets/music/            Local Pixabay tracks (you supply)
data/                    State: used_puzzles.json, last_template.txt
scripts/                 One-time helpers
.github/workflows/       Daily cron
```

---

## One-time setup

### 1. Clone + install
```bash
git clone https://github.com/mrmay06/one-last-quiz.git
cd one-last-quiz
pip install -r requirements.txt
cd remotion && npm install && cd ..
```

### 2. Download BG music
Add 30 mysterious/ambient tracks (MP3, royalty-free from Pixabay) to `assets/music/`. The picker chooses one randomly per run.

### 3. Get YouTube refresh token
1. Create a Google Cloud project → enable **YouTube Data API v3**
2. Create OAuth 2.0 Client ID (**Desktop app**) → download as `scripts/client_secret.json`
3. Run:
   ```bash
   python scripts/get_refresh_token.py
   ```
4. Sign in with the channel's Google account → token prints to terminal.

### 4. Add GitHub secrets
Settings → Secrets → Actions:

| Secret | Required |
|---|---|
| `GEMINI_API_KEY` | ✅ |
| `POLLINATIONS_API_KEY` | ✅ |
| `YOUTUBE_CLIENT_ID` | ✅ |
| `YOUTUBE_CLIENT_SECRET` | ✅ |
| `YOUTUBE_REFRESH_TOKEN` | ✅ |
| `FACEBOOK_ENABLED` | optional (set `true` to enable) |
| `FACEBOOK_PAGE_ID` | optional |
| `FACEBOOK_PAGE_ACCESS_TOKEN` | optional |

### 5. First run
Actions tab → **Daily Video Generation** → **Run workflow** → verify the video lands on YouTube (initially set `privacyStatus` to `unlisted` in `upload_youtube.py` for testing if you want to preview).

---

## Local testing

```bash
# Just the script generation
python -m src.script_gen

# Full pipeline minus uploads (writes tmp/output.mp4)
python -m src.orchestrator --skip-upload

# Preview templates in Remotion Studio
cd remotion && npm run studio
```

---

## Schedule

Two crons in `.github/workflows/daily.yml`:
- `30 20 * * *` UTC = 02:00 IST
- `0 1 * * *` UTC = 06:30 IST

Each run = 1 video.

---

## Costs

| Item | Cost |
|---|---|
| Gemini 2.5 Flash (script + TTS) | ~$0.005/run |
| Pollinations | free tier |
| Remotion render | free (GitHub Actions) |
| YouTube API | free (1600 units/upload, 10k/day quota) |
| **Total** | **< $1/month for 2/day** |

---

## Adding a new channel (template reuse)

The pipeline is content-agnostic. To create a different channel (e.g. "History Facts" or a Hindi version):

1. Fork this repo
2. Edit `prompts/script_system.md` — change topic + tone
3. Edit `prompts/voice_style.md` — change narrator personality
4. Edit `remotion/src/templates/` — adjust visuals/branding
5. Update channel name + secrets

The orchestrator, image gen, voice gen, render, and upload code never changes.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `No .mp3 tracks in assets/music/` | Add MP3s to `assets/music/` |
| Gemini JSON parse errors | Check `data/errors.log`; retries handle most cases |
| Pollinations returns HTML error | Falls back to Gemini Image automatically |
| Remotion render hangs on Actions | `npx remotion browser ensure` step pulls Chrome — re-run |
| YouTube `quotaExceeded` | 1600 units/upload × 6 = daily ceiling. Hard limit. |

---

## Out of scope (do not add without PRD update)
- Instagram / TikTok publishing
- Comment automation
- Analytics dashboards
- Database (JSON-only by design)
- AI video gen (Veo/Kling)

---

Built with the One Last Quiz PRD v1.0.
