from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum, auto


class ValidationResult(StrEnum):
    """The possible results of validating an object"""

    valid = auto()
    invalid = auto()


@dataclass
class IndividualValidationResult:
    """Result from validation"""

    name: StrEnum = field(metadata={"description": "The name of the validator"})
    description: str
    result: ValidationResult

    details: str = field(
        default="", metadata={"description": "Details on the validation"}
    )


@dataclass
class AsValidationResult:
    '''
    Turns a method into a method returning a IndividualValidationResult

    ```python
    >>> class MyEnum(StrEnum):
    ...     test = auto()
    >>> @AsValidationResult(MyEnum.test)
    ... def method(obj: dict) -> str:
    ...     """docstring"""
    ...     return "Failure"
    >>> method({})
    IndividualValidationResult(name=<MyEnum.test: 'test'>,
        description='docstring',
        result=<ValidationResult.invalid: 'invalid'>,
        details='Failure')

    ```
    '''

    name: StrEnum

    def __call__(self, method: Callable[[dict], str | None]):
        def inner(obj: dict):
            result = method(obj)
            docs = method.__doc__ if method.__doc__ else "-- docstring missing --"
            if result is None:
                return IndividualValidationResult(
                    self.name, result=ValidationResult.valid, description=docs
                )

            return IndividualValidationResult(
                self.name,
                result=ValidationResult.invalid,
                details=result,
                description=docs,
            )

        return inner


class Validator:
    """Used to build validators. Usage

    ```python
    validator = Validator()
    @validator.add
    def my_validator(obj: dict) -> IndividualValidationResult:
        ...
    ```

    In the following doctest, the result is an empty set as no validator
    was added.

    ```python
    >>> validator = Validator()
    >>> obj_to_validate = {}
    >>> validator(obj_to_validate)
    []

    ```
    """

    validators: list[Callable[[dict], IndividualValidationResult]]

    def __init__(self):
        self.validators = []

    def add(self, validator):
        self.validators.append(validator)
        return validator

    def __call__(self, obj: dict):
        return [validator(obj) for validator in self.validators]
