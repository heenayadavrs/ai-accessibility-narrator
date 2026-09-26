from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import NarrationSession, get_db
from app.schemas import QATurnOut, SegmentOut, SessionOut

router = APIRouter(tags=["sessions"])


@router.get("/api/sessions/{session_id}", response_model=SessionOut)
def get_session(session_id: str, db: Session = Depends(get_db)) -> SessionOut:
    session = db.get(NarrationSession, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    segments = [
        SegmentOut(
            index=s.ordinal,
            type=s.segment_type.value if hasattr(s.segment_type, "value") else str(s.segment_type),
            text=s.text,
            audio_url=f"/media/{Path(s.audio_path).name}" if s.audio_path else None,
            start_ms=s.start_ms,
            end_ms=s.end_ms,
            order=s.ordinal + 1,
        )
        for s in session.segments
    ]
    turns = [
        QATurnOut(
            id=t.id,
            question=t.question,
            answer=t.answer,
            audio_url=f"/media/{Path(t.audio_path).name}" if t.audio_path else None,
        )
        for t in session.qa_turns
    ]
    return SessionOut(
        session_id=session.id,
        source_type=session.source_type.value,
        source_ref=session.source_ref,
        caption=session.caption,
        parse_status=session.parse_status,
        privacy_mode=session.privacy_mode,
        segments=segments,
        qa_turns=turns,
    )
