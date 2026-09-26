from __future__ import annotations

import shutil
import time
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import NarrationSegment, NarrationSession, QATurn, SegmentType, SourceType, get_db
from app.runtime import get_captioner, get_tts, get_vqa
from app.schemas import AskRequest, AskResponse, ImageNarrateResponse, SegmentOut
from app.services.ocr import extract_text
from app.services.segmentation import split_sentences

router = APIRouter(tags=["image"])


def _audio_url(path: Path | None) -> str | None:
    if path is None:
        return None
    return f"/media/{path.name}"


@router.post("/api/narrate/image", response_model=ImageNarrateResponse)
async def narrate_image(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ImageNarrateResponse:
    settings = get_settings()
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    started = time.perf_counter()
    session_id = str(uuid4())
    suffix = Path(image.filename or "upload.png").suffix or ".png"
    upload_path = settings.upload_dir / f"{session_id}{suffix}"
    with upload_path.open("wb") as out:
        shutil.copyfileobj(image.file, out)

    try:
        captioner = get_captioner()
        tts = get_tts()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    caption = captioner.caption(upload_path)
    ocr_text = extract_text(upload_path)
    if ocr_text and len(ocr_text) > 8:
        # Append a conservative OCR note only when text is clearly present.
        caption = f"{caption.rstrip('.')} Visible text includes: {ocr_text[:200]}."
        if not caption[0].isupper():
            caption = caption[0].upper() + caption[1:]
    elif caption and not caption[0].isupper():
        caption = caption[0].upper() + caption[1:]

    sentences = split_sentences(caption) or [caption]
    session = NarrationSession(
        id=session_id,
        source_type=SourceType.image,
        source_ref=str(upload_path),
        privacy_mode="local",
        caption=caption,
    )
    db.add(session)

    segments_out: list[SegmentOut] = []
    cursor_ms = 0
    for idx, sentence in enumerate(sentences):
        audio_path, _, duration_ms = tts.synthesize(sentence, session_id=session_id)
        start_ms = cursor_ms
        end_ms = cursor_ms + duration_ms
        cursor_ms = end_ms
        seg = NarrationSegment(
            session_id=session_id,
            ordinal=idx,
            segment_type=SegmentType.caption,
            text=sentence,
            audio_path=str(audio_path),
            start_ms=start_ms,
            end_ms=end_ms,
        )
        db.add(seg)
        segments_out.append(
            SegmentOut(
                index=idx,
                type="caption",
                text=sentence,
                audio_url=_audio_url(audio_path),
                start_ms=start_ms,
                end_ms=end_ms,
                order=idx + 1,
            )
        )

    db.commit()
    latency_ms = int((time.perf_counter() - started) * 1000)
    return ImageNarrateResponse(
        session_id=session_id,
        caption=caption,
        segments=segments_out,
        runtime="local",
        latency_ms=latency_ms,
    )


@router.post("/api/narrate/image/ask", response_model=AskResponse)
async def ask_about_image(body: AskRequest, db: Session = Depends(get_db)) -> AskResponse:
    session = db.get(NarrationSession, body.session_id)
    if session is None or session.source_type != SourceType.image:
        raise HTTPException(status_code=404, detail="Image session not found")
    image_path = Path(session.source_ref)
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Session image file missing")

    try:
        vqa = get_vqa()
        tts = get_tts()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    answer = vqa.ask(image_path, body.question.strip())
    audio_path, _, _ = tts.synthesize(answer, session_id=session.id)
    turn = QATurn(
        session_id=session.id,
        question=body.question.strip(),
        answer=answer,
        audio_path=str(audio_path),
    )
    db.add(turn)

    # Also append an answer segment for optional read-along of the answer.
    next_ordinal = len(session.segments)
    db.add(
        NarrationSegment(
            session_id=session.id,
            ordinal=next_ordinal,
            segment_type=SegmentType.answer,
            text=answer,
            audio_path=str(audio_path),
            start_ms=0,
            end_ms=0,
        )
    )
    db.commit()
    return AskResponse(answer=answer, audio_url=_audio_url(audio_path), session_id=session.id)
