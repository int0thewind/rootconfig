# `base-config`

`base-config` library provides a convenient interface to parse, manage,
and export essential parameters in a Python project.
This measure of managing parameters can be used in projects like machine learning,
where various sets of hyper-parameters are experimented on a same code base.

The core of `base-config` is an abstract [Python `dataclass`](https://docs.python.org/library/dataclasses.html)
called `BaseConfig`, which can be inherited to construct your own project configuration class.
The usage of `BaseConfig` class is the same to any Python `dataclass`.
You can add attributes with type annotation directly to it.

## Core Usage

<!-- TODO: provide code examples after the project is finished. -->

```python
from dataclasses import dataclass

from base_confg import BaseConfig


@dataclass
class Config(BaseConfig):
    learning_rate: float
    optimizer: Literal['AdamW', 'RMSProp']
    margin: Fraction

    transform: Any

```

## Caveats

- Custom literals for an attribute are not supported.
  - All variables should use underscore `_` instead of hyphen `-`.
- Literal type annotation, such as `typing.Any`, is not supported.

## Export to/Import from a Text File

JSON is the first-class citizen in text-serialization support.
Configuration classes that inherit `BaseConfig` can be exported to a JSON file
or imported from a JSON file.

## `dataclass` decorator arguments

## Command-line Argument Parsing

## Type Support and Checking

Since JSON is firstly supported, configuration class attributes must be JSON-serializable
and be able to restored from a JSON file.
According to [Python `json` module](https://docs.python.org/library/json.html) in Python's standard library,
the following types can be converted by default.

- Literal types: `str`, `float`, `int`, `bool`, and `NoneType`.
- Sequence type: `list`.
- Mapping type: `dict`.

Other types may be supported as well. See those sub-sections below for more information.

### Supported Non-generic Types

On top of these types, the following Python types defined in
[Python `typing` module](https://docs.python.org/library/typing.html)
are also supported.

- `Union`: poly-type support.
  - `Optional`: essentially `Union[..., NoneType]`.
- `Literal`: can only take specified values and must be one of the type defined above.
- `Any`: no type restriction, but must be one of the type defined above.

### Supported Sequence Types

Only `list` is supported by Python `json` module.
Other sequence types like `tuple` will be automatically converted to `list`.
This may be failed if strict type checking is enabled.
It is recommended to always use `list` for sequence type.

### Numerical Types Support

To allow better number support, `BaseConfig` supports Python complex numbers, fractions, not-a-number, positive infinite, and negative infinite.

Since JSON has no native support for the extended numerical types, they are supported with additional implementations.

Supports for Python complex numbers and fractions are implemented in JSON objects with additional fields demonstrated below.

```JSON
{
    "a_complex_number": {
        "__base_config_numerical_type__": true,
        "real": 1.23,
        "imag": 2.34,
    },
    "a_fraction": {
        "__base_config_numerical_type__": true,
        "numerator": 1,
        "denominator": 2,
    }
}
```

Supports for not-a-number, positive infinite, and negative infinite are implemented with JSON string literals.
Here is how `nan`, `inf`, and `-inf` are converted to JSON.

```
float('nan') --> "NaN"
float('inf') --> "Infinity"
float('+inf') --> "Infinity"
float('-inf') --> "-Infinity"
```

Since those additional formats may collide with some of your existing data,
all additional numerical value supports can be toggled.

Adding support for Python complex numbers, fractions, not-a-number, positive infinite, and negative infinite allows `BaseConfig` to fully support
[Python `numbers` module](https://docs.python.org/library/numbers.html).
All four numerical types: `Complex`, `Real`, `Rational`, and `Integral` can be used to mark attributes in a `BaseConfig` instance.

As for now, Python `Decimal` is not supported.

### A Note on Mapping Type

Caveats on mapping type:

1. Command-line support would not be enabled if a mapping instance is included.
2. So far, nested dataclass is not supported.
