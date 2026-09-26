from __future__ import annotations

from pathlib import Path

try:
    import pytesseract
    from PIL import Image

    _HAS_TESSERACT = True
except Exception:  # noqa: BLE001
    _HAS_TESSERACT = False


def extract_text(image_path: Path) -> str:
    """Optional OCR for text-rich images. Returns empty string if unavailable."""
    if not _HAS_TESSERACT:
        return ""
    try:
        image = Image.open(image_path).convert("RGB")
        text = pytesseract.image_to_string(image) or ""
        return " ".join(text.split())
    except Exception:  # noqa: BLE001
        return ""
