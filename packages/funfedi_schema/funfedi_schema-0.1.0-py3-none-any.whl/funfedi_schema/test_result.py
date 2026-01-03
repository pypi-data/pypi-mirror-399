from enum import StrEnum, auto
from .result import AsValidationResult, IndividualValidationResult, ValidationResult


class MyNames(StrEnum):
    my_name = auto()


@AsValidationResult(MyNames.my_name)
def some_method(obj: dict):
    """Just some method"""
    return None if len(obj) > 0 else "object is empty"


def test_as_result_invalid():
    result = some_method({})

    assert isinstance(result, IndividualValidationResult)
    assert result.result == ValidationResult.invalid
    assert result.details == "object is empty"
    assert result.description == "Just some method"


def test_as_result_valid():
    result = some_method({"key": "valid"})

    assert isinstance(result, IndividualValidationResult)
    assert result.result == ValidationResult.valid
