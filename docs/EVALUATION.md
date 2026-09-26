# Evaluation notes

## Fixture sets
See `data/` for image_manifest, vqa_pairs, and web_pages fixtures.

## Automated results (this workspace)
- Backend `pytest`: **11 passed**
- Webpage order eval: W01–W04 `ok`, W05 `partial` (expected) → `reports/web_order_eval.csv`
- Frontend axe + keyboard smoke: **2 passed** (`PLAYWRIGHT_BASE_URL=http://localhost:3001 npm run test:a11y`)
- Live API smoke: image narration ~3.6s, VQA answer “It appears blue.”, page fixture segments ordered

## Manual (demo gate)
- [ ] Keyboard-only walkthrough of image + webpage flows
- [ ] NVDA announces controls and play status meaningfully
- [ ] Browser network tab: no image bytes to third-party AI hosts (only `localhost:8000`)
- [ ] Impairment preview shows non-clinical disclaimer
- [ ] Privacy panel shows **Local processing** when `/api/health` reports `runtime: local`

## Privacy verification procedure
1. Open DevTools → Network
2. Drop a demo image and wait for narration
3. Confirm requests go only to `localhost:8000` / `127.0.0.1:8000`
4. Confirm no requests to `api.openai.com`, `api.anthropic.com`, `generativelanguage.googleapis.com`, etc., carrying image payloads

## NVDA pass log
Date: _pending before live demo_
Tester: _pending_
Findings: _record defects and fixes here_

### Suggested NVDA checklist
- Tab order reaches Image/Webpage tabs, Choose Image, Play/Pause, Ask, Preview toggles
- `aria-live` status announces play/pause/section changes
- Highlighted segment is programmatically exposed (`aria-current`)
- Error alerts (`role="alert"`) are spoken
