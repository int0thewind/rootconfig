# `baseconfig`

`baseconfig` library provides a convenient interface to parse, manage,
and export essential parameters in a Python project.
This measure of managing parameters can be used in projects like machine learning,
where various sets of hyper-parameters are experimented on a same code base.

The core of `baseconfig` is an abstract [Python `dataclass`](https://docs.python.org/library/dataclasses.html)
called `BaseConfig`, which can be inherited to construct your own project configuration class.
The usage of `BaseConfig` class is the same to any Python `dataclass`.
You can add attributes with type annotation directly to it.

## Core Usage

```python
from dataclasses import dataclass
from fractions import Fraction

from baseconfig import BaseConfig


@dataclass
class Config(BaseConfig):
    learning_rate: float
    optimizer: Literal['AdamW', 'SGD']
    margin: Fraction


config = Config.parse_args()
# OR
config = Config.from_json('path/to/json')
```
