# Product Requirements Document (PRD)

## Personas
- **Priya** — needs concise image narration and follow-up Q&A
- Same user — needs navigable audio reading of dense articles
- **Vikram** — sighted reviewer using impairment preview for empathy/demo

## Core flows
1. Image: drop → caption → TTS segments → synced highlight → ask → VQA → speak answer
2. Webpage: URL → parse → ordered typed segments → audio → highlight
3. Impairment preview: blur / reduced color / high contrast over the same content (non-clinical)

## Functional requirements
FR1–FR10 as defined in the master spec (upload, local caption, TTS timings, player controls, VQA, page parse, highlight, impairment preview, keyboard access, privacy status).

## Non-functional
Local-first privacy, semantic accessibility, measured latency, useful errors, transparent runtime status.
