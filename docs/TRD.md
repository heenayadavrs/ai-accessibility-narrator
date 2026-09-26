# Technical Requirements Document (TRD)

## Stack
- Frontend: Next.js App Router + TypeScript (`:3000`)
- Backend: FastAPI + Python 3.11 (`:8000`)
- Models: BLIP captioning, BLIP VQA, Piper TTS (local)
- Web: BeautifulSoup + optional Playwright
- OCR stretch: Tesseract
- Orchestration: Docker Compose

## API
- `GET /api/health`
- `POST /api/narrate/image`
- `POST /api/narrate/image/ask`
- `POST /api/narrate/page`
- `GET /api/sessions/{session_id}`
- `GET /media/{file}.wav`

## Data model
`narration_sessions`, `narration_segments`, `qa_turns` (SQLite).

## Sync
MVP is segment-level: one WAV per segment; highlight advances on audio `ended`.

## Privacy
No third-party AI endpoints receive image bytes. URL fetch is documented separately from local inference.
