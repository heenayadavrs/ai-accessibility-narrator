# Third-Party Notices — AI Accessibility Narrator

Built with local, open components and pinned model assets. No paid AI API is required for the MVP.

## Models

### Salesforce BLIP image captioning (`Salesforce/blip-image-captioning-base`)
- License: BSD-3-Clause (per Hugging Face model card)
- Source: https://huggingface.co/Salesforce/blip-image-captioning-base
- Used for: local image caption generation

### Salesforce BLIP VQA (`Salesforce/blip-vqa-base`)
- License: BSD-3-Clause (per Hugging Face model card)
- Source: https://huggingface.co/Salesforce/blip-vqa-base
- Used for: scoped visual question answering

### Hugging Face Transformers BLIP implementation
- License: Apache-2.0
- Source: https://github.com/huggingface/transformers

### Piper TTS (software)
- License: MIT
- Source: https://github.com/rhasspy/piper

### Piper voice `en_US-libritts-high`
- Dataset: LibriTTS (OpenSLR 60) — **CC BY 4.0**
- Source: https://huggingface.co/rhasspy/piper-voices (en/en_US/libritts/high)
- MODEL_CARD notes training from scratch on train-clean-360
- This project downloads the voice at warm-up time and does **not** vendor the `.onnx` binary in git
- Earlier candidate `en_US-lessac-medium` was rejected: its Blizzard 2013 / Lessac source data is research-only and not suitable for redistribution

## Libraries (selected)

| Component | License (typical) | Role |
|-----------|-------------------|------|
| FastAPI | MIT | Backend API |
| Next.js | MIT | Frontend |
| BeautifulSoup4 | MIT | HTML parsing |
| Playwright | Apache-2.0 | Optional page rendering |
| Tesseract / pytesseract | Apache-2.0 | Optional OCR |
| PyTorch | BSD-style | Local inference |
| Atkinson Hyperlegible | SIL Open Font License 1.1 | UI typography |

## Privacy note

Image bytes are processed only by local model runtimes in the MVP. Fetching a user-supplied webpage URL is network activity performed by the local backend and is separate from AI inference.
