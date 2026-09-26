from __future__ import annotations

from app.config import get_settings

_captioner = None
_vqa = None
_tts = None
_status: dict[str, dict] = {
    "captioning": {"ready": False, "detail": "not loaded"},
    "vqa": {"ready": False, "detail": "not loaded"},
    "tts": {"ready": False, "detail": "not loaded"},
}


def get_model_status() -> dict[str, dict]:
    return _status


def load_models() -> None:
    """Load local models into module singletons. Safe to call multiple times."""
    global _captioner, _vqa, _tts
    settings = get_settings()

    try:
        from app.services.captioning import CaptioningService

        _captioner = CaptioningService(settings.caption_model_id)
        _status["captioning"] = {"ready": True, "detail": settings.caption_model_id}
    except Exception as exc:  # noqa: BLE001
        _status["captioning"] = {"ready": False, "detail": str(exc)}

    try:
        from app.services.vqa import VQAService

        _vqa = VQAService(settings.vqa_model_id)
        _status["vqa"] = {"ready": True, "detail": settings.vqa_model_id}
    except Exception as exc:  # noqa: BLE001
        _status["vqa"] = {"ready": False, "detail": str(exc)}

    try:
        from app.services.tts import TTSService

        _tts = TTSService(
            voice_dir=settings.piper_voice_dir,
            voice_name=settings.piper_voice_name,
            audio_dir=settings.audio_dir,
        )
        _status["tts"] = {"ready": True, "detail": settings.piper_voice_name}
    except Exception as exc:  # noqa: BLE001
        _status["tts"] = {"ready": False, "detail": str(exc)}


def get_captioner():
    if _captioner is None:
        raise RuntimeError("Captioning model is not loaded")
    return _captioner


def get_vqa():
    if _vqa is None:
        raise RuntimeError("VQA model is not loaded")
    return _vqa


def get_tts():
    if _tts is None:
        raise RuntimeError("TTS model is not loaded")
    return _tts
