from jsonschema import validate
import requests

from .load import load_schema, load_example, load_invalid
from .data.webfinger import webfinger_data

example1 = load_example("application_jrd_json", "1")
example2 = load_example("application_jrd_json", "2")
example3 = load_example("application_jrd_json", "3")
example4 = load_example("application_jrd_json", "4")
invalid1 = load_invalid("application_jrd_json", 1)


def verify_url(url: str):
    response = requests.get(url, headers={"accept": "application/jrd+json"})
    errors = []

    if not response.headers["content-type"].startswith("application/jrd+json"):
        errors += [
            f"""incorrect response content-type {response.headers["content-type"]}"""
        ]
        print(errors)

    schema = load_schema("application-jrd-json")

    try:
        validate(instance=response.json(), schema=schema)
    except Exception as e:
        print(e)
        errors += ["Validation failed"]

    result = "✅" if len(errors) == 0 else "❌"

    return result, errors


def build_url(acct_uri: str) -> str:
    """
    ```python
    >>> build_url("acct:cow_says_moo@dev.bovine.social")
    'https://dev.bovine.social/.well-known/webfinger?resource=acct:cow_says_moo@dev.bovine.social'

    ```
    """

    domain = acct_uri.split("@")[1]

    return f"https://{domain}/.well-known/webfinger?resource={acct_uri}"


def verify_webfinger():
    table_lines = [
        "| name | acct_uri | result |",
        "| --- | --- | --- |",
    ]

    for item in webfinger_data:
        result, _ = verify_url(build_url(item.acct))

        table_lines.append(f"| {item.name} | {item.acct} | {result} |")

    return "\n".join(table_lines)
