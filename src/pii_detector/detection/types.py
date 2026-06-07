from dataclasses import dataclass
from enum import Enum

class EntityType(str, Enum):
    """A category of PII the detector can recognize."""

    EMAIL = "EMAIL"
    PHONE = "PHONE"

@dataclass(frozen=True)
class Entity:
    """A single detected PII span.
    
    This is the detector's *internal* representation. The API layer maps it to 
    its own response schema, so we can evolve internal fields (confidence,
    source layer, ...) without changing the public contract.
    """

    type: EntityType
    value: str
    start: int
    end: int