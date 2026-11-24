"""Kokoro local TTS: availability gating, metadata, and output contract."""

import sys
import types

import numpy as np
import pytest

from tools.audio import kokoro_tts
from tools.audio.kokoro_tts import KokoroTTS
from tools.base_tool import ToolStatus


@pytest.fixture(autouse=True)
def _reset_engine():
    KokoroTTS._engine = None
    yield
    KokoroTTS._engine = None


def test_metadata():
    info = KokoroTTS().get_info()
    assert info["name"] == "kokoro_tts"
    assert info["capability"] == "tts"
    assert info["provider"] == "kokoro"
    assert KokoroTTS().estimate_cost({"text": "hi"}) == 0.0


def test_unavailable_without_model_files(monkeypatch, tmp_path):
    monkeypatch.setenv("KOKORO_MODEL_DIR", str(tmp_path))
    assert KokoroTTS().get_status() == ToolStatus.UNAVAILABLE
    result = KokoroTTS().execute({"text": "hello"})
    assert not result.success
    assert "not available" in result.error


def test_generates_wav_with_fake_engine(monkeypatch, tmp_path):
    (tmp_path / kokoro_tts.MODEL_FILE).write_bytes(b"")
    (tmp_path / kokoro_tts.VOICES_FILE).write_bytes(b"")
    monkeypatch.setenv("KOKORO_MODEL_DIR", str(tmp_path))

    calls = {}

    class FakeKokoro:
        def __init__(self, model, voices):
            calls["paths"] = (model, voices)

        def get_voice_style(self, name):
            return np.ones((1, 4), dtype=np.float32)

        def create(self, text, voice, speed, lang):
            calls.update(text=text, voice=voice, speed=speed, lang=lang)
            return np.zeros(24000, dtype=np.float32), 24000

    monkeypatch.setitem(sys.modules, "kokoro_onnx", types.SimpleNamespace(Kokoro=FakeKokoro))
    pytest.importorskip("soundfile")

    out = tmp_path / "narration" / "line.wav"
    result = KokoroTTS().execute({"text": "The ledger opens.", "voice": "bm_george", "output_path": str(out)})

    assert result.success, result.error
    assert out.is_file()
    assert calls["lang"] == "en-gb"
    assert calls["voice"] == "bm_george"
    assert result.data["audio_duration_seconds"] == 1.0
    assert result.artifacts == [str(out)]
