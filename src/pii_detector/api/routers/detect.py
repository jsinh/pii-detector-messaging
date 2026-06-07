from fastapi import APIRouter

from pii_detector.api.schemas import DetectRequest, DetectResponse
from pii_detector.detection.pipeline import Pipeline

router = APIRouter(tags=["detection"])

# Single pipeline instance shared across requests. When the detection layers
# load models at startup, this moves into the app lifespan + a FastAPI
# dependency; for the stub a module-level instance is enough.
_pipeline = Pipeline()


@router.post("/detect", response_model=DetectResponse)
def detect_pii(request: DetectRequest) -> DetectResponse:
    """Detect PII entities in a message.

    The pipeline is currently a stub returning no entities; the contract is
    live so clients can integrate now and gain detections as the layers land.
    """
    entities = _pipeline.detect(request.text)
    return DetectResponse.from_domain(entities)
