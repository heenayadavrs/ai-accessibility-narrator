from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


class SourceType(str, enum.Enum):
    image = "image"
    webpage = "webpage"


class SegmentType(str, enum.Enum):
    caption = "caption"
    heading = "heading"
    paragraph = "paragraph"
    link = "link"
    button = "button"
    image_alt = "image_alt"
    answer = "answer"
    warning = "warning"


class NarrationSession(Base):
    __tablename__ = "narration_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType), nullable=False)
    source_ref: Mapped[str] = mapped_column(Text, nullable=False, default="")
    privacy_mode: Mapped[str] = mapped_column(String(64), default="local")
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    parse_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    segments: Mapped[list[NarrationSegment]] = relationship(
        "NarrationSegment", back_populates="session", cascade="all, delete-orphan", order_by="NarrationSegment.ordinal"
    )
    qa_turns: Mapped[list[QATurn]] = relationship(
        "QATurn", back_populates="session", cascade="all, delete-orphan", order_by="QATurn.created_at"
    )


class NarrationSegment(Base):
    __tablename__ = "narration_segments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(ForeignKey("narration_sessions.id"), nullable=False)
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    segment_type: Mapped[SegmentType] = mapped_column(Enum(SegmentType), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    audio_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_ms: Mapped[int] = mapped_column(Integer, default=0)
    end_ms: Mapped[int] = mapped_column(Integer, default=0)

    session: Mapped[NarrationSession] = relationship("NarrationSession", back_populates="segments")


class QATurn(Base):
    __tablename__ = "qa_turns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(ForeignKey("narration_sessions.id"), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    audio_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped[NarrationSession] = relationship("NarrationSession", back_populates="qa_turns")


settings = get_settings()
# SQLAlchemy needs sqlite:/// with three slashes for absolute paths on Linux
_db_url = settings.database_url
engine = create_engine(_db_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    from pathlib import Path

    settings.audio_dir.mkdir(parents=True, exist_ok=True)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    db_path = settings.database_url.replace("sqlite:///", "")
    if db_path and not db_path.startswith(":memory:"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
