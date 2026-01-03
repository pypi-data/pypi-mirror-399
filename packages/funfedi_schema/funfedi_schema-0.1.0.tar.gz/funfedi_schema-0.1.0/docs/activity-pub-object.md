# ActivityPub object

* [ActivityPub Object](./assets/activity-pub-object.schema.json)


```python
>>> from jsonschema import validate
>>> from tools import load_schema, dump
>>> from tools.activity_pub_object import *
>>> schema = load_schema("activity-pub-object")

```


## Examples

These examples are taken from [ActivityPub](https://www.w3.org/TR/activitypub/). We note that this specification contains
quite a few invalid examples due to missing ids.

```python
>>> validate(instance=examples["4_part"], schema=schema)
>>> validate(instance=examples["6_part"], schema=schema)
>>> validate(instance=examples["7_part"], schema=schema)

```

??? Example "Example 4_part"

    ```json
    --8<-- "./examples/activity_pub/example4_part.json"
    ```

??? Example "Example 6_part"

    ```json
    --8<-- "./examples/activity_pub/example6_part.json"
    ```

??? Example "Example 7_part"

    ```json
    --8<-- "./examples/activity_pub/example7_part.json"
    ```

### Mastodon

```python
>>> validate(instance=mastodon1, schema=schema)
Traceback (most recent call last): 
...
jsonschema.exceptions.ValidationError: None is not of type 'string'
...
Failed validating 'type' in schema['properties']['summary']:
    {'description': 'The summary of the object', 'type': 'string'}

On instance['summary']:
    None
```

After removing null values, it is valid.

```python
>>> non_null = {k: v for k, v in mastodon1.items() if v}
>>> validate(instance=non_null, schema=schema)

```

??? Example "Mastodon1"

    ```json
    --8<-- "./examples/mastodon/example1.json"
    ```