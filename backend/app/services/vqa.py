from __future__ import annotations

from pathlib import Path

from PIL import Image
from transformers import BlipForQuestionAnswering, BlipProcessor


HEDGE_PHRASES = (
    "i can't determine",
    "i cannot determine",
    "unclear",
    "not sure",
    "difficult to determine",
    "unable to",
)


class VQAService:
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.processor = BlipProcessor.from_pretrained(model_id)
        self.model = BlipForQuestionAnswering.from_pretrained(model_id)
        self.model.eval()

    def ask(self, image_path: Path, question: str) -> str:
        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(images=image, text=question, return_tensors="pt")
        out = self.model.generate(**inputs, max_new_tokens=40)
        answer = self.processor.decode(out[0], skip_special_tokens=True).strip()
        return self._normalize(answer, question)

    def _normalize(self, answer: str, question: str) -> str:
        if not answer:
            return "I can't determine that from the visible evidence."
        lower = answer.lower().strip()
        # BLIP often returns short fragments; phrase them as spoken answers.
        if lower in {"n/a", "none", "unknown", "null"}:
            return "I can't determine that from the visible evidence."
        if any(p in lower for p in HEDGE_PHRASES):
            return answer if answer.endswith(".") else f"{answer}."
        q = question.lower()
        if "color" in q and "appear" not in lower:
            answer = f"It appears {answer}" if not answer.lower().startswith("the ") else answer
            if "appear" not in answer.lower():
                answer = answer.replace(" is ", " appears ", 1) if " is " in answer else f"The color appears {answer}"
        if not answer.endswith((".", "!", "?")):
            answer = f"{answer}."
        # Capitalize first letter
        return answer[0].upper() + answer[1:]
