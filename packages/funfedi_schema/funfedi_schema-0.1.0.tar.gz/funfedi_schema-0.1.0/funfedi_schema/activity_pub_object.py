from enum import StrEnum, auto
import json
from jsonschema import ValidationError, validate
from pyld import jsonld

from funfedi_schema import schema
from .result import AsValidationResult, Validator


class ActivityPubObjectValidators(StrEnum):
    schema = auto()
    schema_after_normalization = auto()
    activity_streams_json_ld_compacted = auto()


activity_pub_object_validator = Validator()
"""Validator for ActivityPub objects

```python
activity_pub_object_validator({"activity pub": "object as dictionary"})
```
"""


def _result_against_schema(obj: dict):
    try:
        validate(instance=obj, schema=schema.activity_pub_object)
        return None
    except ValidationError as e:
        return e.message


@activity_pub_object_validator.add
@AsValidationResult(ActivityPubObjectValidators.schema)
def validate_activity_pub_object_against_schema(
    obj: dict,
):
    """Validates the document against the [Funfedi ActivityPub Object Schema](https://schemas.funfedi.dev/activity-pub-object/)."""
    return _result_against_schema(obj)


@activity_pub_object_validator.add
@AsValidationResult(ActivityPubObjectValidators.schema_after_normalization)
def validate_activity_pub_object_against_schema_after_normalization(
    obj: dict,
):
    """First normalizes the object by removing null values. Then turns `to` and `cc` to list if they
    are a single string. Then validates the document against the [Funfedi ActivityPub Object Schema](https://schemas.funfedi.dev/activity-pub-object/)."""
    new_obj = {key: value for key, value in obj.items() if value}
    if isinstance(new_obj.get("to"), str):
        new_obj["to"] = [new_obj["to"]]
    if isinstance(new_obj.get("cc"), str):
        new_obj["cc"] = [new_obj["cc"]]

    return _result_against_schema(new_obj)


@activity_pub_object_validator.add
@AsValidationResult(ActivityPubObjectValidators.activity_streams_json_ld_compacted)
def validate_as_json_ld(obj: dict):
    """Checks that the object matches its compacted form, i.e.

    ```python
    assert jsonld.compact(obj, obj["context"]) == obj
    ```

    This criterion is due to [Activity Streams 2.0, Section 2.1 JSON-LD](https://www.w3.org/TR/activitystreams-core/#jsonld)

    > The serialized JSON form of an Activity Streams 2.0 document MUST be consistent with what would be produced by the standard JSON-LD 1.0 Processing Algorithms and API [JSON-LD-API] Compaction Algorithm using, at least, the normative JSON-LD @context definition provided here.

    We are not certain that we understand Activity Streams 2.0 correctly. For example, the provided
    examples have different content values when expanded. This confuses us.
    """
    context = obj.get("@context")
    if context is None:
        return "No context found"

    try:
        new_obj = jsonld.compact(obj, context)
    except Exception:
        return "JSON-LD compaction failed"

    if not isinstance(new_obj, dict):
        return "JSON-LD Compaction did not result in a dictionary"

    if new_obj == obj:
        return

    from dictdiffer import diff

    return json.dumps(list(diff(obj, new_obj)), indent=2)
