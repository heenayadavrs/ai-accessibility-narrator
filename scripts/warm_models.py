#!/usr/bin/env python3
"""Pre-download BLIP captioning, BLIP VQA, and the pinned Piper voice."""

from __future__ import annotations

import argparse
import os
import urllib.request
from pathlib import Path


CAPTION_MODEL = "Salesforce/blip-image-captioning-base"
VQA_MODEL = "Salesforce/blip-vqa-base"
PIPER_VOICE = "en_US-libritts-high"
PIPER_BASE = (
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts/high"
)


def download_piper(voice_dir: Path) -> None:
    voice_dir.mkdir(parents=True, exist_ok=True)
    files = [
        f"{PIPER_VOICE}.onnx",
        f"{PIPER_VOICE}.onnx.json",
    ]
    for name in files:
        dest = voice_dir / name
        if dest.exists() and dest.stat().st_size > 1000:
            print(f"[skip] {dest}")
            continue
        url = f"{PIPER_BASE}/{name}"
        print(f"[download] {url} -> {dest}")
        urllib.request.urlretrieve(url, dest)
    # Voice MODEL_CARD: LibriTTS dataset is CC BY 4.0 (OpenSLR 60).
    print(f"[ok] Piper voice ready in {voice_dir}")


def download_hf_models() -> None:
    from transformers import BlipForConditionalGeneration, BlipForQuestionAnswering, BlipProcessor

    print(f"[download] {CAPTION_MODEL}")
    BlipProcessor.from_pretrained(CAPTION_MODEL)
    BlipForConditionalGeneration.from_pretrained(CAPTION_MODEL)
    print(f"[download] {VQA_MODEL}")
    BlipProcessor.from_pretrained(VQA_MODEL)
    BlipForQuestionAnswering.from_pretrained(VQA_MODEL)
    print("[ok] Hugging Face models cached")


def main() -> None:
    parser = argparse.ArgumentParser(description="Warm local model caches")
    parser.add_argument(
        "--piper-dir",
        default=os.environ.get("PIPER_VOICE_DIR", "piper_voices"),
        type=Path,
    )
    parser.add_argument("--skip-hf", action="store_true")
    parser.add_argument("--skip-piper", action="store_true")
    args = parser.parse_args()

    if not args.skip_piper:
        download_piper(args.piper_dir)
    if not args.skip_hf:
        download_hf_models()
    print("Warm-up complete.")


if __name__ == "__main__":
    main()
