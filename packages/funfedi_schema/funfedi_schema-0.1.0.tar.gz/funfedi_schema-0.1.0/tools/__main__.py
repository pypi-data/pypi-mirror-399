from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
import click


from .application_jrd_json import verify_webfinger


@dataclass
class config:
    filename: str
    method: Callable


@click.command
def main():
    table = [config(filename="webfinger.md", method=verify_webfinger)]

    Path("snippets").mkdir(exist_ok=True)

    for item in table:
        result = item.method()
        with open(f"snippets/{item.filename}", "w") as fp:
            fp.write(result)


if __name__ == "__main__":
    main()
