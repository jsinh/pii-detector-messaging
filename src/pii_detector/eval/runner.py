"""CLI entry point for the evaluation framework.

Loads a gold JSONL dataset, runs the detection pipeline over each example, and
prints a per-entity-type report plus the compliance-weighted cost.

Run it via the console script::

    pii-eval data/eval/sample.jsonl
    pii-eval data/eval/sample.jsonl --cost-ratio 20
"""

from __future__ import annotations

import argparse
from pathlib import Path

from pii_detector.core.config import get_settings
from pii_detector.detection.pipeline import Pipeline
from pii_detector.eval.datasets import load_jsonl
from pii_detector.eval.metrics import evaluate


def run(dataset_path: Path, fn_fp_cost_ratio: float) -> int:
    """Evaluate the pipeline against ``dataset_path`` and print the report."""
    examples = load_jsonl(dataset_path)
    pipeline = Pipeline()
    pairs = [(example.entities, pipeline.detect(example.text)) for example in examples]
    report = evaluate(pairs, fn_fp_cost_ratio=fn_fp_cost_ratio)

    print(f"Dataset: {dataset_path}  ({len(examples)} examples)")
    print(f"{'TYPE':<10} {'PREC':>6} {'RECALL':>7} {'F1':>6}  {'TP':>4} {'FP':>4} {'FN':>4}")
    for entity_type, score in report.per_type.items():
        print(
            f"{entity_type.value:<10} "
            f"{score.precision:>6.2f} {score.recall:>7.2f} {score.f1:>6.2f}  "
            f"{score.true_positives:>4} {score.false_positives:>4} {score.false_negatives:>4}"
        )
    print(f"\nWeighted cost (FN penalised {fn_fp_cost_ratio:g}x FP): {report.weighted_cost:g}")
    return 0


def main() -> None:
    """Parse arguments and run the evaluation."""
    settings = get_settings()
    parser = argparse.ArgumentParser(description="Run PII detection evaluation.")
    parser.add_argument("dataset", type=Path, help="Path to a JSONL gold dataset.")
    parser.add_argument(
        "--cost-ratio",
        type=float,
        default=settings.fn_fp_cost_ratio,
        help="False-negative to false-positive cost ratio (default from settings).",
    )
    args = parser.parse_args()
    raise SystemExit(run(args.dataset, args.cost_ratio))


if __name__ == "__main__":
    main()
