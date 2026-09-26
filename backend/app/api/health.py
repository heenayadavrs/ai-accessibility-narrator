from fastapi import APIRouter

from app.config import get_settings
from app.runtime import get_model_status
from app.schemas import HealthResponse, ModelStatus

router = APIRouter(tags=["health"])


@router.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    status_map = get_model_status()
    models = [
        ModelStatus(name=name, ready=info["ready"], detail=info.get("detail"))
        for name, info in status_map.items()
    ]
    all_ready = all(m.ready for m in models) if models else False
    return HealthResponse(
        status="ready" if all_ready else "degraded",
        runtime=settings.runtime_mode,
        privacy_mode="local" if settings.runtime_mode == "local" else settings.runtime_mode,
        models=models,
    )
