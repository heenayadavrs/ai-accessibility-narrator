from pydantic import BaseModel, Field


class SegmentOut(BaseModel):
    index: int
    type: str
    text: str
    audio_url: str | None = None
    start_ms: int = 0
    end_ms: int = 0
    order: int | None = None


class ImageNarrateResponse(BaseModel):
    session_id: str
    caption: str
    segments: list[SegmentOut]
    runtime: str = "local"
    latency_ms: int | None = None


class AskRequest(BaseModel):
    session_id: str
    question: str = Field(min_length=1, max_length=500)


class AskResponse(BaseModel):
    answer: str
    audio_url: str | None = None
    session_id: str


class PageNarrateRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)


class PageNarrateResponse(BaseModel):
    session_id: str
    segments: list[SegmentOut]
    parse_status: str = "ok"
    runtime: str = "local"
    warning: str | None = None


class QATurnOut(BaseModel):
    id: str
    question: str
    answer: str
    audio_url: str | None = None


class SessionOut(BaseModel):
    session_id: str
    source_type: str
    source_ref: str
    caption: str | None = None
    parse_status: str | None = None
    privacy_mode: str
    segments: list[SegmentOut]
    qa_turns: list[QATurnOut] = []


class ModelStatus(BaseModel):
    name: str
    ready: bool
    detail: str | None = None


class HealthResponse(BaseModel):
    status: str
    runtime: str
    privacy_mode: str
    models: list[ModelStatus]
