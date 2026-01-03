import json


def load_schema(name: str):
    with open(f"docs/assets/{name}.schema.json") as fp:
        return json.load(fp)


def load_example(name: str, number: str):
    with open(f"examples/{name}/example{number}.json") as fp:
        return json.load(fp)


def load_invalid(name: str, number: int):
    with open(f"examples/{name}/invalid{number}.json") as fp:
        return json.load(fp)
