"""The Detector interface every detection layer implements.

Regex, NER, and LLM layers all satisfy this Protocol, so the pipeline can
compose, reorder, or mock any layer without depending on its concrete type.
"""

from typing import Protocol

from pii_detector.detection.types import Entity


class Detector(Protocol):
    """Anything that can find PII spans in a piece of text."""

    def detect(self, text: str) -> list[Entity]:
        """Return the PII entities found in ``text`` (possibly empty)."""
        ...
