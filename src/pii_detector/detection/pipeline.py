"""The detection pipeline: orchestrates the regex -> NER -> LLM layers.

Stub for now: returns no entities until the individual layers land. It exists
already so the API route and the eval framework can both call the same seam
(`pipeline.detect(text)`) and be built/tested independently of the layers.
"""

from pii_detector.detection.types import Entity


class Pipeline:
    """Runs the configured detection layers and applies routing between them."""

    def detect(self, text: str) -> list[Entity]:
        """Detect PII entities in ``text``.

        TODO: run the regex layer, then the fine-tuned NER, then the LLM
        fallback, applying the compliance-weighted routing logic between them.
        """
        return []