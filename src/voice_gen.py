"""Gemini 2.5 Flash TTS → MP3."""
from __future__ import annotations

import base64
import logging
import struct
import wave
from pathlib import Path

import google.generativeai as genai

from src import config
from src.utils import ensure_tmp, retry

log = logging.getLogger(__name__)


def _load_voice_style() -> str:
    return (config.PROMPTS_DIR / "voice_style.md").read_text()


def _pcm_to_wav(pcm: bytes, out_path: Path, sample_rate: int = 24_000) -> None:
    """Gemini TTS returns raw 16-bit PCM. Wrap in WAV header."""
    with wave.open(str(out_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(pcm)


def _validate_audio(path: Path) -> None:
    if not path.exists() or path.stat().st_size < 5_000:
        raise ValueError(f"audio file missing or too small: {path}")
    # Quick duration check via WAV header
    try:
        with wave.open(str(path), "rb") as wf:
            duration = wf.getnframes() / float(wf.getframerate())
        if duration < config.MIN_VOICE_SECONDS:
            raise ValueError(f"audio too short: {duration:.2f}s")
    except wave.Error:
        # If not WAV (e.g. mp3), skip strict duration check
        pass


@retry(attempts=config.VOICE_RETRIES + 1, base_delay=2.0, exceptions=(Exception,))
def _generate(script: str, out_path: Path) -> None:
    genai.configure(api_key=config.GEMINI_API_KEY)
    style = _load_voice_style()
    prompt = f"{style}\n\nScript to narrate:\n{script}"

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
            _pcm_to_wav(data, out_path)
            _validate_audio(out_path)
            return
    raise RuntimeError("Gemini TTS returned no audio")


def generate_voice(script: str) -> Path:
    """Generate voiceover. Returns path to .wav (Remotion accepts both wav/mp3)."""
    tmp = ensure_tmp()
    out = tmp / "voiceover.wav"
    log.info("Generating voiceover: voice=%s, %d chars", config.DEFAULT_VOICE, len(script))
    _generate(script, out)
    log.info("Voiceover written: %s", out)
    return out
