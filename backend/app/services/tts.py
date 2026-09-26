from __future__ import annotations

import wave
from pathlib import Path
from uuid import uuid4


class TTSService:
    """Local Piper TTS. Falls back to silent WAV placeholders if the voice is missing."""

    def __init__(self, voice_dir: Path, voice_name: str, audio_dir: Path):
        self.voice_dir = Path(voice_dir)
        self.voice_name = voice_name
        self.audio_dir = Path(audio_dir)
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self._voice = None
        self._load_voice()

    def _model_paths(self) -> tuple[Path, Path]:
        onnx = self.voice_dir / f"{self.voice_name}.onnx"
        cfg = self.voice_dir / f"{self.voice_name}.onnx.json"
        return onnx, cfg

    def _load_voice(self) -> None:
        onnx, cfg = self._model_paths()
        if not onnx.exists() or not cfg.exists():
            # Defer hard failure; synthesize() will use silence fallback with a clear marker.
            self._voice = None
            return
        from piper import PiperVoice

        self._voice = PiperVoice.load(str(onnx), config_path=str(cfg))
        # Multi-speaker voices (e.g. libritts) require a speaker id.
        self._speaker_id = 0
        try:
            num = getattr(self._voice.config, "num_speakers", 1) or 1
            if num > 1:
                self._speaker_id = 0
        except Exception:  # noqa: BLE001
            self._speaker_id = 0

    @property
    def ready(self) -> bool:
        return self._voice is not None

    def synthesize(self, text: str, session_id: str | None = None) -> tuple[Path, int, int]:
        """
        Generate one WAV for the given text.
        Returns (path, start_ms=0, end_ms=duration).
        """
        filename = f"{session_id or 'clip'}_{uuid4().hex[:10]}.wav"
        out_path = self.audio_dir / filename

        if self._voice is None:
            self._write_silence(out_path, duration_s=max(1.0, len(text.split()) * 0.35))
        else:
            import wave as wave_mod

            with wave_mod.open(str(out_path), "wb") as wav_file:
                try:
                    self._voice.synthesize(text, wav_file, speaker_id=self._speaker_id)
                except TypeError:
                    # Older piper-tts signatures omit speaker_id.
                    self._voice.synthesize(text, wav_file)

        duration_ms = wav_duration_ms(out_path)
        return out_path, 0, duration_ms

    def _write_silence(self, path: Path, duration_s: float = 1.0, rate: int = 22050) -> None:
        nframes = int(duration_s * rate)
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(rate)
            wf.writeframes(b"\x00\x00" * nframes)


def wav_duration_ms(path: Path) -> int:
    with wave.open(str(path), "rb") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate() or 1
        return int(round(1000.0 * frames / rate))
