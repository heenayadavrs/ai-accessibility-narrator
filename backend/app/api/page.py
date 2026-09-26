from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import NarrationSegment, NarrationSession, SegmentType, SourceType, get_db
from app.runtime import get_tts
from app.schemas import PageNarrateRequest, PageNarrateResponse, SegmentOut
from app.services.segmentation import split_sentences
from app.services.web_extract import fetch_and_extract

router = APIRouter(tags=["page"])

TYPE_MAP = {
    "heading": SegmentType.heading,
    "paragraph": SegmentType.paragraph,
    "link": SegmentType.link,
    "button": SegmentType.button,
    "image_alt": SegmentType.image_alt,
    "warning": SegmentType.warning,
}


@router.post("/api/narrate/page", response_model=PageNarrateResponse)
async def narrate_page(body: PageNarrateRequest, db: Session = Depends(get_db)) -> PageNarrateResponse:
    result = await fetch_and_extract(body.url.strip())
    if result.parse_status == "error" and not result.segments:
        raise HTTPException(status_code=422, detail=result.warning or "Could not parse page")

    try:
        tts = get_tts()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    session_id = str(uuid4())
    session = NarrationSession(
        id=session_id,
        source_type=SourceType.webpage,
        source_ref=body.url.strip(),
        privacy_mode="local",
        parse_status=result.parse_status,
    )
    db.add(session)

    narratable: list[tuple[str, str]] = []
    if result.warning:
        narratable.append(("warning", result.warning))
    for seg in result.segments:
        # Split long paragraphs into sentence-level narration clips
        if seg.type == "paragraph":
            parts = split_sentences(seg.text) or [seg.text]
            for part in parts:
                narratable.append((seg.type, part))
        else:
            narratable.append((seg.type, seg.text))

    segments_out: list[SegmentOut] = []
    cursor_ms = 0
    for idx, (seg_type, text) in enumerate(narratable):
        audio_path, _, duration_ms = tts.synthesize(text, session_id=session_id)
        start_ms = cursor_ms
        end_ms = cursor_ms + duration_ms
        cursor_ms = end_ms
        db.add(
            NarrationSegment(
                session_id=session_id,
                ordinal=idx,
                segment_type=TYPE_MAP.get(seg_type, SegmentType.paragraph),
                text=text,
                audio_path=str(audio_path),
                start_ms=start_ms,
                end_ms=end_ms,
            )
        )
        segments_out.append(
            SegmentOut(
                index=idx,
                type=seg_type,
                text=text,
                audio_url=f"/media/{Path(audio_path).name}",
                start_ms=start_ms,
                end_ms=end_ms,
                order=idx + 1,
            )
        )

    db.commit()
    return PageNarrateResponse(
        session_id=session_id,
        segments=segments_out,
        parse_status=result.parse_status,
        runtime="local",
        warning=result.warning,
    )
