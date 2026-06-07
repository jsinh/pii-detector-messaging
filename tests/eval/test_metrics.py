from pii_detector.detection.types import Entity, EntityType
from pii_detector.eval.metrics import evaluate


def _email(start: int = 0, end: int = 7) -> Entity:
    return Entity(type=EntityType.EMAIL, value="a@b.com", start=start, end=end)


def test_perfect_prediction_scores_one():
    gold = [_email()]
    report = evaluate([(gold, [_email()])], fn_fp_cost_ratio=10.0)
    score = report.per_type[EntityType.EMAIL]
    assert score.precision == 1.0
    assert score.recall == 1.0
    assert score.f1 == 1.0
    assert report.weighted_cost == 0.0


def test_missed_entity_is_a_weighted_false_negative():
    report = evaluate([([_email()], [])], fn_fp_cost_ratio=10.0)
    score = report.per_type[EntityType.EMAIL]
    assert score.recall == 0.0
    assert score.false_negatives == 1
    # one FN, penalised 10x, no FPs
    assert report.weighted_cost == 10.0


def test_spurious_prediction_is_a_false_positive():
    report = evaluate([([], [_email()])], fn_fp_cost_ratio=10.0)
    score = report.per_type[EntityType.EMAIL]
    assert score.precision == 0.0
    assert score.false_positives == 1
    assert report.weighted_cost == 1.0


def test_false_negative_costs_more_than_false_positive():
    fn_report = evaluate([([_email()], [])], fn_fp_cost_ratio=10.0)
    fp_report = evaluate([([], [_email()])], fn_fp_cost_ratio=10.0)
    assert fn_report.weighted_cost > fp_report.weighted_cost
