# AI / Evaluation / Privacy Design

## AI roles
| Component | Role |
|-----------|------|
| BLIP captioning | Automatic scene description without a prompt |
| BLIP VQA | Focused questions on the current image session |
| Piper TTS | Local neural speech; one WAV per segment |
| BeautifulSoup (+ optional Playwright) | Semantic webpage segments |
| Tesseract (optional) | Embedded text in photos |

## Quality posture
Prefer calibrated uncertainty over invention. Low-quality / occluded images should hedge ("appears", "unclear") rather than hallucinate brands or details.

## Privacy
- No third-party AI API receives image bytes in the MVP
- Model warm-up downloads weights once into a local cache / volume
- User-supplied webpage URLs are fetched by the local backend (network activity separate from inference)
- Privacy panel shows **Local processing** only when `/api/health` reports `runtime: local`
