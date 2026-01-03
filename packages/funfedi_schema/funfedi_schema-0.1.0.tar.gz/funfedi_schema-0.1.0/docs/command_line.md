# command line tool

## Installation

Install the package via

```bash
pip install funfedi_schema
```

The funfedi-schema command should then become available.

## Validating an ActivityPub object

Suppose you have an ActivityPub object, e.g.

```json title="./examples/activity_pub/example2.json"
--8<-- "./examples/activity_pub/example2.json"
```

Then one can validate it using the command line tool using

```bash
funfedi-schema validate-activity-pub-object \
    ./examples/activity_pub/example2.json
```

The then generated output is

```bash
schema is invalid
'id' is a required property


schema_after_normalization is invalid
'id' is a required property


activity_streams_json_ld_compacted is invalid
[
  [
    "change",
    "to",
    [
      [
        "https://chatty.example/ben/"
      ],
      "https://chatty.example/ben/"
    ]
  ]
]
```