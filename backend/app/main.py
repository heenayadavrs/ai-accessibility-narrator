from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import health, image, page, sessions
from app.config import get_settings
from app.db import init_db
from app.runtime import load_models


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    init_db()
    settings.audio_dir.mkdir(parents=True, exist_ok=True)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    if settings.load_models_on_startup:
        load_models()
    yield


app = FastAPI(
    title="AI Accessibility Narrator",
    description="Local-first audio narration for images and webpages.",
    version="0.1.0",
    lifespan=lifespan,
)

# Local Next.js may bind 3000, 3001, etc. when ports are busy.
_LOCAL_UI_ORIGINS = [
    f"http://{host}:{port}"
    for host in ("localhost", "127.0.0.1")
    for port in range(3000, 3011)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_LOCAL_UI_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(image.router)
app.include_router(page.router)
app.include_router(sessions.router)

settings = get_settings()
settings.audio_dir.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(settings.audio_dir)), name="media")
