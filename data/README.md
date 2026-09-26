# AI Accessibility Narrator — compact demo dataset

This is a fixed portfolio/demo evaluation set aligned to the FINAL MASTER. It is intentionally small so implementation and interview preparation are not blocked by data collection.

Files:
- `image_manifest.csv`: 13 visual fixtures with expected captions, one seeded VQA question, OCR expectations and quality flags.
- `vqa_pairs.csv`: 20 seeded question/answer pairs across the images.
- `web_pages.csv`: 5 local webpage fixtures with expected reading order.
- `webpages/`: HTML fixtures for semantic parsing and clutter suppression tests.
- `images/`: synthetic visual fixtures; use them as deterministic test fixtures, not as a real-world benchmark.

Recommended use:
1. Start with I01/I06 for image narration + VQA.
2. Add I03/I05/I11/I13/I14 for OCR.
3. Add I08/I12 to demonstrate uncertainty instead of hallucination.
4. Use W01/W02 for webpage extraction and read-along ordering.
5. Use W03/W04 for richer segment types; use W05 for parser/error handling.

The master spec calls for 20–30 curated demo images for deeper evaluation. This pack deliberately gives you a compact first set; expand later only when the core product is stable.
