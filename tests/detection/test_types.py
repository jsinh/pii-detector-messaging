import pytest

from pii_detector.detection.types import Entity, EntityType


def test_entity_holds_span_and_type():
    entity = Entity(type=EntityType.EMAIL, value="a@b.com", start=0, end=7)
    assert entity.type is EntityType.EMAIL
    assert entity.value == "a@b.com"
    assert (entity.start, entity.end) == (0, 7)


def test_entity_is_frozen():
    entity = Entity(type=EntityType.PHONE, value="555-0100", start=0, end=8)
    with pytest.raises(AttributeError):
        entity.value = "changed"  # type: ignore[misc]


def test_entity_type_value_is_stable_string():
    assert EntityType.EMAIL.value == "EMAIL"
    assert EntityType.PHONE.value == "PHONE"
