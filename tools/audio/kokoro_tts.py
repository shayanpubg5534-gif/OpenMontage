"""Kokoro-82M local text-to-speech provider tool (ONNX, CPU-friendly).

Kokoro is an Apache-2.0 82M-parameter TTS model. It runs faster than real
time on a plain CPU and sounds markedly more natural than Piper, which makes
it the best free/offline narration voice OpenMontage can drive without a GPU
or an API key.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    RetryPolicy,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)

MODEL_FILE = "kokoro-v1.0.onnx"
VOICES_FILE = "voices-v1.0.bin"
DEFAULT_VOICE = "am_michael"


def _model_dir() -> Path:
    return Path(os.environ.get("KOKORO_MODEL_DIR", Path.home() / ".cache" / "kokoro"))


def _lang_for_voice(voice: str) -> str:
    # Kokoro voice ids are prefixed <lang><gender>_: a=American, b=British.
    return "en-gb" if voice.startswith("b") else "en-us"


class KokoroTTS(BaseTool):
    name = "kokoro_tts"
    version = "0.1.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "kokoro"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = ["python:kokoro_onnx", "python:soundfile"]
    install_instructions = (
        "Install Kokoro (free, offline, CPU):\n"
        "  pip install kokoro-onnx soundfile\n"
        "Then download the model files (~350 MB) into ~/.cache/kokoro "
        "(or set KOKORO_MODEL_DIR):\n"
        "  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
        f"{MODEL_FILE}\n"
        "  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
        f"{VOICES_FILE}"
    )
    agent_skills = ["text-to-speech"]

    capabilities = [
        "text_to_speech",
        "offline_generation",
    ]
    supports = {
        "voice_cloning": False,
        "multilingual": False,
        "offline": True,
        "native_audio": True,
    }
    best_for = [
        "natural-sounding free narration without a GPU or API key",
        "long-form documentary voiceover at zero marginal cost",
    ]
    not_good_for = [
        "voice clone matching",
        "fine-grained emotional direction",
    ]
    fallback_tools = ["piper_tts"]

    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {"type": "string"},
            "voice": {
                "type": "string",
                "default": DEFAULT_VOICE,
                "description": (
                    "Kokoro voice id, e.g. am_michael, am_onyx, am_adam, "
                    "bm_george, bm_lewis, af_heart, bf_emma. Voices may be "
                    "blended as 'am_michael:60,bm_george:40'."
                ),
            },
            "speed": {"type": "number", "default": 1.0, "minimum": 0.5, "maximum": 2.0},
            "lang": {
                "type": "string",
                "description": "Phonemizer language; inferred from the voice prefix when omitted.",
            },
            "output_path": {"type": "string"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=4, ram_mb=1500, vram_mb=0, disk_mb=400, network_required=False
    )
    retry_policy = RetryPolicy(max_retries=1, retryable_errors=[])
    idempotency_key_fields = ["text", "voice", "speed", "lang"]
    side_effects = ["writes audio file to output_path"]
    user_visible_verification = ["Listen to generated audio for pacing and pronunciation"]

    _engine = None

    def get_status(self) -> ToolStatus:
        try:
            import kokoro_onnx  # noqa: F401
            import soundfile  # noqa: F401
        except ImportError:
            return ToolStatus.UNAVAILABLE
        d = _model_dir()
        if (d / MODEL_FILE).is_file() and (d / VOICES_FILE).is_file():
            return ToolStatus.AVAILABLE
        return ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def _load(self):
        if KokoroTTS._engine is None:
            from kokoro_onnx import Kokoro

            d = _model_dir()
            KokoroTTS._engine = Kokoro(str(d / MODEL_FILE), str(d / VOICES_FILE))
        return KokoroTTS._engine

    def _resolve_voice(self, engine, voice: str):
        if ":" not in voice and "," not in voice:
            return voice
        # Weighted blend, e.g. "am_michael:60,bm_george:40".
        import numpy as np

        parts = []
        for chunk in voice.split(","):
            vid, _, weight = chunk.strip().partition(":")
            parts.append((vid.strip(), float(weight or 1)))
        total = sum(w for _, w in parts)
        return sum(engine.get_voice_style(v) * (w / total) for v, w in parts).astype(np.float32)

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        if self.get_status() != ToolStatus.AVAILABLE:
            return ToolResult(success=False, error="Kokoro TTS not available. " + self.install_instructions)

        start = time.time()
        try:
            import soundfile as sf

            engine = self._load()
            voice = inputs.get("voice") or DEFAULT_VOICE
            first_voice = voice.split(",")[0].split(":")[0].strip()
            lang = inputs.get("lang") or _lang_for_voice(first_voice)
            samples, sample_rate = engine.create(
                inputs["text"],
                voice=self._resolve_voice(engine, voice),
                speed=float(inputs.get("speed", 1.0)),
                lang=lang,
            )
            output_path = Path(inputs.get("output_path", "tts_output.wav"))
            output_path.parent.mkdir(parents=True, exist_ok=True)
            sf.write(str(output_path), samples, sample_rate)
        except Exception as exc:
            return ToolResult(success=False, error=f"Kokoro TTS generation failed: {exc}")

        audio_seconds = round(len(samples) / sample_rate, 3)
        return ToolResult(
            success=True,
            data={
                "provider": self.provider,
                "model": "kokoro-v1.0",
                "voice": voice,
                "lang": lang,
                "text_length": len(inputs["text"]),
                "audio_duration_seconds": audio_seconds,
                "output": str(output_path),
                "format": "wav",
            },
            artifacts=[str(output_path)],
            model="kokoro-v1.0",
            duration_seconds=round(time.time() - start, 2),
        )
