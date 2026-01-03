from glob import glob
import json

import click

from .result import ValidationResult

from .activity_pub_object import activity_pub_object_validator


def activity_pub_objects():
    for filename in glob("test_data/created_object_*.json"):
        app_name = filename.split("_")[-1].removesuffix(".json")
        with open(filename) as f:
            data = json.load(f)

        yield app_name, data


@click.group
def main(): ...


@main.command
def validate_all_activity_pub_objects():
    for name, data in activity_pub_objects():
        result = activity_pub_object_validator(data)
        print(
            f"{name:<20} passed: "
            + ", ".join((x.name for x in result if x.result == ValidationResult.valid))
        )


@main.command
@click.argument("file", type=click.File("r"))
def validate_activity_pub_object(file):
    """Displays detailed validation of the ActivityPub object given by file. File is supposed to be"""
    content = file.read()
    data = json.loads(content)

    result = activity_pub_object_validator(data)

    for x in result:
        print(f"{x.name} is {x.result}")
        if x.result == ValidationResult.invalid:
            print(x.details)
            print()
            print()


if __name__ == "__main__":
    main()
