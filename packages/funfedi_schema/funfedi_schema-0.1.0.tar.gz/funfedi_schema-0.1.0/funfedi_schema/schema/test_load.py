from . import load_schema


def test_load():
    result = load_schema("activity-pub-object")

    assert isinstance(result, dict)
