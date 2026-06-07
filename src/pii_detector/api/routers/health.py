from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/")
def root() -> dict[str, str]:
    """Liveness: the process is up and serving."""
    return {"status": "ok"}


@router.get("/healthz")
def healthz() -> dict[str, str]:
    """Liveness probe (process is alive)."""
    return {"status": "ok"}


@router.get("/readyz")
def readyz() -> dict[str, str]:
    """Readiness probe (service can handle traffic).

    Today this is trivially ok. Once the NER layer loads a model at startup,
    this will report 'ready' only after that load completes.
    """
    return {"status": "ready"}
