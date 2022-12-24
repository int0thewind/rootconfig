![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rootconfig)

# `rootconfig`

`rootconfig` library provides a convenient interface to parse, manage,
and export essential parameters in a Python project.
This measure of managing parameters can be used in projects like machine learning,
where various sets of hyper-parameters are experimented on a same code base.

The core of `rootconfig` is an abstract [Python `dataclass`](https://docs.python.org/library/dataclasses.html)
called `RootConfig`, which can be inherited to construct your own project configuration class.
The usage of `RootConfig` class is the same to any Python `dataclass`.
You can declare attributes with type annotation.

## Basic Usage

To use the `RootConfig` class, inherit it decorate it with `dataclass`.

```python
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Literal

from rootconfig import RootConfig


@dataclass
class Config(RootConfig):
    optimizer: Literal['AdamW', 'SGD']
    margin: Fraction
    learning_rate: float = 1e-4
    flags: list[bool] = field(
        default_factory=lambda: [True]
    )
```

You may directly create an instance.

```python
config = Config('SGD', learning_rate=float('nan'), margin=Fraction('4/3'), flags=[False])
```

You may parse command-line arguments. All arguments are keyword arguments.

```python
config = Config.parse_args()  # defaults to sys.argv[1:]
# OR
config = Config.parse_args([
    # '--learning-rate', '1e-4',  # default values can be safely omitted.
    '--optimizer', 'AdamW',  # `Literal` arguments can be parsed.
    '--margin', '3/4',  # `Fraction` can be instantiated from a string. e.g. Fraction('3/4')
    '--flags', 'True', 'False'  # A sequence of `bool` is supported by its Python literal.
])
# OR
parser = ...  # You have your own Python's `ArgumentParser` instance.
config = Config.parse_args(parser=parser)  # Use your own parser.
```

We offer first-class support to Python's `Fraction`, `Decimal`, `complex`, `Path`, and `bool`.
`list` type can be safely parsed either by providing multiple values.

You may import from JSON files.

```python
config = Config.from_json(Path('/path/to/file'))
```

...and you may export to a JSON file.

```python
config.to_json(Path('/path/to/file'))
```

Non-serializable types like `Fraction`, `Decimal`, `complex`, and `Path`
can be safely imported and exported with special JSON `Object` structure.
`nan`, `inf`, and `-inf` are also supported.

## Type Supports

`RootConfig` automatically check variable types when being instantiated.
If there are unsupported types or values do not match with their types,
an `TypeError` would be raised.

To fully support JSON import/export and Python's `ArgumentParser`,
`dataclass` fields may only have the following types.

- String-convertable singleton types:
  - `int`
  - `Fraction`
  - `Decimal`
  - `float`
  - `complex`
  - `str`
  - `Path`
- Singleton types that do not have one-to-one mapping with strings:
  - `bool`: to support `bool` in Python's `ArgumentParser`,
    we explictely asked you to supply "True" or "False".
    So far, we haven't consider `ArgumentParser` action `store_true` or `store_false`.
- Others
  - `Literal`
    - From Python's [`typing` module](https://docs.python.org/3.10/library/typing.html#typing.Literal),
      supplied literals must be hashable.
      Type arguments for "Literal" must be `None` or a literal value (`int`, `bool`, or `str`).
    - All literals must be in the same type.
  - `list`
    - `list` type can only accept singleton types aformentioned. `Literal` type cannot be accepted.

Supporting new types may cause some trouble to JSON serialization or `ArgumentParser`.
For instance, it is very hard to parse an dictionary in command-line,
so, there is no support to `dict`.
We may add support to some other types in the future,
but a treadoff to some features may be introduced.
