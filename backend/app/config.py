from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT = Path(__file__).resolve().parents[2]
_BACKEND = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    runtime_mode: str = "local"
    load_models_on_startup: bool = True
    database_url: str = f"sqlite:///{(_BACKEND / 'storage' / 'narrator.db').as_posix()}"
    audio_dir: Path = _BACKEND / "storage" / "audio"
    upload_dir: Path = _BACKEND / "storage" / "uploads"
    piper_voice_dir: Path = _ROOT / "piper_voices"
    piper_voice_name: str = "en_US-libritts-high"
    data_dir: Path = _ROOT / "data"
    hf_home: Path = Path.home() / ".cache" / "huggingface"
    caption_model_id: str = "Salesforce/blip-image-captioning-base"
    vqa_model_id: str = "Salesforce/blip-vqa-base"
    max_page_bytes: int = 2_000_000
    page_fetch_timeout_s: float = 15.0
    min_static_text_chars: int = 40


@lru_cache
def get_settings() -> Settings:
    return Settings()
