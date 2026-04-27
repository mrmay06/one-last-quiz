"""Whisper-based forced alignment → word-level timestamps for kinetic captions.

Uses faster-whisper (CTranslate2 backend) — runs on CPU, ~5x realtime for short clips.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import TypedDict

log = logging.getLogger(__name__)

_model = None  # lazy-loaded


class WordTiming(TypedDict):
    word: str
    start: float
    end: float


def _get_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        # 'tiny.en' is enough for clean Gemini TTS — fast, ~75MB
        log.info("Loading Whisper model (tiny.en) — first run downloads ~75MB")
        _model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
    return _model


def align(audio_path: Path) -> list[WordTiming]:
    """Transcribe + word-align the audio. Returns list of {word, start, end}."""
    model = _get_model()
    segments, _ = model.transcribe(
        str(audio_path),
        word_timestamps=True,
        vad_filter=False,
        beam_size=1,
    )
    words: list[WordTiming] = []
    for seg in segments:
        if not seg.words:
            continue
        for w in seg.words:
            words.append({"word": w.word.strip(), "start": w.start, "end": w.end})
    log.info("Captions: %d words aligned", len(words))
    return words
