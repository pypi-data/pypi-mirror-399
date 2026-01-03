from .result import ValidationResult
from .activity_pub_object import (
    ActivityPubObjectValidators,
    activity_pub_object_validator,
)

obj = {
    "@context": [
        "https://www.w3.org/ns/activitystreams",
    ],
    "attributedTo": "http://host.test/users/admin",
    "cc": ["http://host.test/users/admin/followers"],
    "content": "<p>Some message</p>",
    "id": "http://host.test/objects/some/id",
    "published": "2025-12-30T12:00:00Z",
    "to": ["https://www.w3.org/ns/activitystreams#Public"],
    "type": "Note",
}


def test_activity_pub_obj_validator():
    result = activity_pub_object_validator(obj)

    result_map = {r.name: r for r in result}

    assert (
        result_map[ActivityPubObjectValidators.schema].result == ValidationResult.valid
    )
    assert (
        result_map[ActivityPubObjectValidators.schema_after_normalization].result
        == ValidationResult.valid
    )
    assert (
        result_map[
            ActivityPubObjectValidators.activity_streams_json_ld_compacted
        ].result
        == ValidationResult.invalid
    )


def test_activity_pub_obj_validator_compacted():
    new_obj = {**obj}
    new_obj["to"] = "as:Public"
    new_obj["cc"] = obj["cc"][0]
    new_obj["@context"] = obj["@context"][0]

    result = activity_pub_object_validator(new_obj)

    result_map = {r.name: r for r in result}

    assert (
        result_map[ActivityPubObjectValidators.schema].result
        == ValidationResult.invalid
    )
    assert (
        result_map[ActivityPubObjectValidators.schema_after_normalization].result
        == ValidationResult.valid
    )
    assert (
        result_map[
            ActivityPubObjectValidators.activity_streams_json_ld_compacted
        ].result
        == ValidationResult.valid
    )
