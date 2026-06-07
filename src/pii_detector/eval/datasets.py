"""Loaders for evaluation datasets (gold + adversarial).

Datasets are JSONL: one JSON object per line, each with a ``text`` string and an
``entities`` list of ``{type, value, start, end}`` objects. Example line::

    {"text": "email me at a@b.com", "entities": [
        {"type": "EMAIL", "value": "a@b.com", "start": 12, "end": 19}]}
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from pii_detector.detection.types import Entity, EntityType


@dataclass(frozen=True)
class GoldExample:
    """A single labelled message: the text and its known PII spans."""

    text: str
    entities: list[Entity]


def load_jsonl(path: Path) -> list[GoldExample]:
    """Load gold examples from a JSONL file.

    Raises:
        FileNotFoundError: if ``path`` does not exist.
        ValueError: if any line is malformed (with the line number).
    """
    examples: list[GoldExample] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                entities = [
                    Entity(
                        type=EntityType(item["type"]),
                        value=item["value"],
                        start=item["start"],
                        end=item["end"],
                    )
                    for item in record.get("entities", [])
                ]
                examples.append(GoldExample(text=record["text"], entities=entities))
            except (KeyError, ValueError) as exc:
                raise ValueError(f"{path}:{line_no}: invalid record: {exc}") from exc
    return examples
