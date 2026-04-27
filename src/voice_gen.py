"""Gemini 2.5 Flash TTS → WAV → ffmpeg speedup → final voiceover.

Returns (path, duration_seconds) so the renderer can size the video to the voice.
"""
from __future__ import annotations

import base64
import logging
import shutil
import subprocess
import wave
from pathlib import Path

import google.generativeai as genai

from src import config
from src.utils import ensure_run_dir, retry

log = logging.getLogger(__name__)


def _load_voice_style() -> str:
    return (config.PROMPTS_DIR / "voice_style.md").read_text()


def _pcm_to_wav(pcm: bytes, out_path: Path, sample_rate: int = 24_000) -> None:
    with wave.open(str(out_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm)


def _wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())


def _validate(path: Path) -> float:
    if not path.exists() or path.stat().st_size < 5_000:
        raise ValueError(f"audio missing or too small: {path}")
    duration = _wav_duration(path)
    if duration < config.MIN_VOICE_SECONDS:
        raise ValueError(f"audio too short: {duration:.2f}s")
    return duration


def _atempo(in_path: Path, out_path: Path, speed: float) -> None:
    """Speed up audio by `speed` factor using ffmpeg atempo (pitch preserved)."""
    if not shutil.which("ffmpeg"):
        log.warning("ffmpeg not found — skipping atempo speedup")
        shutil.copy2(in_path, out_path)
        return
    cmd = [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-i",
        str(in_path),
        "-filter:a",
        f"atempo={speed}",
        str(out_path),
    ]
    subprocess.run(cmd, check=True)


@retry(attempts=config.VOICE_RETRIES + 1, base_delay=2.0, exceptions=(Exception,))
def _generate(script: str, raw_path: Path) -> None:
    genai.configure(api_key=config.GEMINI_API_KEY)
    style = _load_voice_style()
    prompt = f"{style}\n\nNarrate this exactly:\n{script}"

    model = genai.GenerativeModel(config.GEMINI_TTS_MODEL)
    resp = model.generate_content(
        prompt,
        generation_config={
            "response_modalities": ["AUDIO"],
            "speech_config": {
                "voice_config": {
                    "prebuilt_voice_config": {"voice_name": config.DEFAULT_VOICE}
                }
            },
        },
    )
    for part in resp.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data and part.inline_data.data:
            data = part.inline_data.data
            if isinstance(data, str):
                data = base64.b64decode(data)
            _pcm_to_wav(data, raw_path)
            return
    raise RuntimeError("Gemini TTS returned no audio")


def generate_voice(script: str) -> tuple[Path, float]:
    """Generate voiceover and apply post-processing speedup.
    Returns (final_path, duration_seconds)."""
    run_dir = ensure_run_dir()
    raw = run_dir / "voiceover_raw.wav"
    final = run_dir / "voiceover.wav"

    log.info("TTS: voice=%s, script=%d chars", config.DEFAULT_VOICE, len(script))
    _generate(script, raw)
    _validate(raw)

    _atempo(raw, final, config.VOICE_SPEED)
    raw.unlink(missing_ok=True)
    duration = _validate(final)
    log.info("Voiceover: %.2fs (after %.2fx speedup)", duration, config.VOICE_SPEED)
    return final, duration
