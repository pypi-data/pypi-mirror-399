# application/jrd+json

* [application/jrd+json schema](./assets/application-jrd-json.schema.json)

This page tests the `application/jrd+json` schema using python and doctests.
Some convenience methods are included from tools.

```python
>>> from jsonschema import validate
>>> from tools import load_schema, dump
>>> from tools.application_jrd_json import *
>>> schema = load_schema("application-jrd-json")

```

## Background on the format

The `application/jrd+json` format is defined in [RFC 7033 Webfinger](https://www.rfc-editor.org/rfc/rfc7033.html).
RFC 7033 in turns reference [RFC 6415 Web Host Metadata](https://www.rfc-editor.org/rfc/rfc6415)
for the definition of the format. RFC 6415 delegates the definition further
to the OASIS standard
[Extensible Resource Descriptor (XRD) Version 1.0](https://docs.oasis-open.org/xri/xrd/v1.0/xrd-1.0.html).


## Validation of the wild

The following examples check that the result of the webfinger request conforms
to schema and has the content type `application/jrd+json`.

--8<-- "snippets/webfinger.md"

### Adding additional applications.

This can be done by editing [data/webfinger](https://codeberg.org/funfedidev/schemas/src/branch/main/tools/data/webfinger.py)
and opening a pull request.

## Examples

These example are taken from [RFC 7033](https://www.rfc-editor.org/rfc/rfc7033.html)

```python
>>> validate(instance=example1, schema=schema)
>>> validate(instance=example2, schema=schema)
>>> validate(instance=example3, schema=schema)
>>> validate(instance=example4, schema=schema)

```

??? Example "Example 1"

    ```json
    --8<-- "./examples/application_jrd_json/example1.json"
    ```

??? Example "Example 2"

    ```json
    --8<-- "./examples/application_jrd_json/example2.json"
    ```
??? Example "Example 3"

    ```json
    --8<-- "./examples/application_jrd_json/example3.json"
    ```

??? Example "Example 4"

    ```json
    --8<-- "./examples/application_jrd_json/example4.json"
    ```


## Invalid examples


```python
>>> validate(instance=invalid1, schema=schema)
Traceback (most recent call last): 
...
jsonschema.exceptions.ValidationError: None is not of type 'object'

```

??? Example "Invalid Example 1"

    ```json
    --8<-- "./examples/application_jrd_json/invalid1.json"
    ```
