import json

from .load import load_schema

__all__ = ["load_schema", "dump"]


def dump(data):
    print(json.dumps(data, indent=2))
