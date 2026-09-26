from __future__ import annotations

from pathlib import Path

from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor


UNCERTAIN_HINTS = (
    "blurry",
    "dark",
    "unclear",
    "low light",
    "low-light",
    "occluded",
    "hidden",
    "partial",
)


class CaptioningService:
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.processor = BlipProcessor.from_pretrained(model_id)
        self.model = BlipForConditionalGeneration.from_pretrained(model_id)
        self.model.eval()

    def caption(self, image_path: Path) -> str:
        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt")
        out = self.model.generate(**inputs, max_new_tokens=60)
        text = self.processor.decode(out[0], skip_special_tokens=True).strip()
        return self._hedge(text)

    def _hedge(self, caption: str) -> str:
        lower = caption.lower()
        if any(h in lower for h in UNCERTAIN_HINTS):
            if "unclear" not in lower and "difficult" not in lower:
                return f"{caption.rstrip('.')}; some details are difficult to determine."
        if caption and not caption.lower().startswith(("a ", "the ", "an ", "this ", "it ")):
            caption = f"The image shows {caption}"
        if not caption.endswith((".", "!", "?")):
            caption = f"{caption}."
        return caption
