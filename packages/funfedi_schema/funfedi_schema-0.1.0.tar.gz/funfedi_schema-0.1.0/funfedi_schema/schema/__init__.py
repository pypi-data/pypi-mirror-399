import json
from pathlib import Path


def load_schema(name: str):
    directory = Path(__file__).parent
    filename = directory / f"{name}.schema.json"

    with open(filename) as f:
        return json.load(f)


activity_pub_object = load_schema("activity-pub-object")
