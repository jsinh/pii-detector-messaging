from pydantic import BaseModel, Field

from pii_detector.detection.types import Entity, EntityType


class DetectRequest(BaseModel):
    """Request body for POST /detect."""

    text: str = Field(min_length=1, description="The message text to scan for PII.")


class DetectEntity(BaseModel):
    """A single detected PII entity in the response."""

    type: EntityType
    value: str
    start: int
    end: int

    @classmethod
    def from_domain(cls, entity: Entity) -> "DetectEntity":
        """Map an internal domain Entity to its public API representation."""
        return cls(
            type=entity.type,
            value=entity.value,
            start=entity.start,
            end=entity.end,
        )


class DetectResponse(BaseModel):
    """Response body for POST /detect."""

    entities: list[DetectEntity]

    @classmethod
    def from_domain(cls, entities: list[Entity]) -> "DetectResponse":
        """Build the response from the detector's domain output."""
        return cls(entities=[DetectEntity.from_domain(e) for e in entities])
