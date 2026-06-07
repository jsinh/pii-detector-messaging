"""Compliance-weighted evaluation metrics.

Per-entity-type precision/recall (deliberately never collapsed into one
aggregate score) plus a weighted cost in which a false negative is penalised
``fn_fp_cost_ratio`` times as much as a false positive. See the README section
"The eval framework" for why the asymmetry matters.

Span matching is currently *exact*: a prediction counts as a true positive only
if its (type, start, end) matches a gold span exactly. Fuzzy / overlap-based
matching is a deliberate later refinement.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from pii_detector.detection.types import Entity, EntityType


def _span_key(entity: Entity) -> tuple[EntityType, int, int]:
    return (entity.type, entity.start, entity.end)


@dataclass(frozen=True)
class EntityScore:
    """Precision/recall counts for a single entity type."""

    entity_type: EntityType
    true_positives: int
    false_positives: int
    false_negatives: int

    @property
    def precision(self) -> float:
        denom = self.true_positives + self.false_positives
        return self.true_positives / denom if denom else 0.0

    @property
    def recall(self) -> float:
        denom = self.true_positives + self.false_negatives
        return self.true_positives / denom if denom else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0


@dataclass(frozen=True)
class EvalReport:
    """The full evaluation result: per-type scores plus the weighted cost."""

    per_type: dict[EntityType, EntityScore]
    fn_fp_cost_ratio: float

    @property
    def weighted_cost(self) -> float:
        """Total compliance cost; each FN counts ``fn_fp_cost_ratio`` x an FP."""
        false_positives = sum(s.false_positives for s in self.per_type.values())
        false_negatives = sum(s.false_negatives for s in self.per_type.values())
        return false_positives + self.fn_fp_cost_ratio * false_negatives


def evaluate(
    examples: list[tuple[list[Entity], list[Entity]]],
    fn_fp_cost_ratio: float,
) -> EvalReport:
    """Score ``(gold, predicted)`` pairs into a per-entity-type report.

    Args:
        examples: one ``(gold_entities, predicted_entities)`` tuple per message.
        fn_fp_cost_ratio: how many false positives one false negative is "worth".
    """
    true_positives: dict[EntityType, int] = defaultdict(int)
    false_positives: dict[EntityType, int] = defaultdict(int)
    false_negatives: dict[EntityType, int] = defaultdict(int)

    for gold, predicted in examples:
        gold_keys = {_span_key(e) for e in gold}
        pred_keys = {_span_key(e) for e in predicted}
        for key in pred_keys:
            entity_type = key[0]
            if key in gold_keys:
                true_positives[entity_type] += 1
            else:
                false_positives[entity_type] += 1
        for key in gold_keys - pred_keys:
            false_negatives[key[0]] += 1

    seen_types = set(true_positives) | set(false_positives) | set(false_negatives)
    per_type = {
        entity_type: EntityScore(
            entity_type=entity_type,
            true_positives=true_positives[entity_type],
            false_positives=false_positives[entity_type],
            false_negatives=false_negatives[entity_type],
        )
        for entity_type in sorted(seen_types, key=lambda t: t.value)
    }
    return EvalReport(per_type=per_type, fn_fp_cost_ratio=fn_fp_cost_ratio)
