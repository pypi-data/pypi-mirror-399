# nanokv

A compact(er) key-value serialization format for Python.

## Installation

```bash
pip install nanokv
```

## Usage

```python
import nanokv

# Serialize a dict to a string
s = nanokv.dumps({"name": "example", "count": 42})
# => '[name="example",count=42]'

# Parse a string to a dict
d = nanokv.loads('[name="example",count=42]')
# => {"name": "example", "count": 42}
```

## Format

```
[key="value",count=123,nested=[a=1,b=2],list={1,2,3}]
```

- Strings are quoted: `"value"`
- Integers are bare: `123`
- Booleans are bare: `true` | `false`
- Nested objects use brackets: `[key=value]`
- Lists use braces: `{1,2,3}`

## Grammar

See [GRAMMAR](GRAMMAR.ebnf) for the full specification.
