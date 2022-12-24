"""
`RootConfig`: Project configuration management
with command-line argument parsing and JSON import/export.
"""

import json
import os
from abc import ABC
from argparse import ArgumentParser
from dataclasses import MISSING, asdict, dataclass, fields, is_dataclass
from decimal import Decimal
from fractions import Fraction
from itertools import pairwise
from pathlib import Path
from typing import Any, Literal, get_args, get_origin

supported_string_covertable_types: set[type] = {
    int, Fraction, Decimal, float, complex,
    str, Path,
}
"""Supported string-convertable types.

These types are not container types,
and their instances one-to-one string representation
that can be converted to or from.

```python
str(Fraction('3/4')) == '3/4'
str(complex('3.2+nanj')) == '3.2+nanj'
```
"""

supported_singleton_types: set[type] = {
    bool
} | supported_string_covertable_types
"""Supported singleton types.

These types are not container types,
but the addition of `bool` type breaks one-to-one string conversion.
"""

supported_types: set[type] = {
    Literal, list,
} | supported_singleton_types
"""All supported types in `RootConfig` class"""


def parse_bool(literal: str):
    """Parse boolean literals.

    Python `bool` does not convert 'False' to `False`.
    This function is created for Python `ArgumentParser.add_argument()`'s
    `type` argument to receive 'True' as `True` and 'False' as `False`.

    ```python
    parser.add_argument('--foo', type=parse_bool)
    ```
    """
    if literal.lower() == 'true':
        return True
    elif literal.lower() == 'false':
        return False
    raise ValueError(f'"{literal}" is a malformed boolean string.')


_JSON_CUSTOM_TYPE_KEY = '__custom_type__'
_JSON_CUSTOM_TYPE_VALUE = '__value__'


class RootConfigJSONEncoder(json.JSONEncoder):
    """Custom Python `json.JSONEncoder` to encode non-standard type
    such as `complex`, `Decimal`, `Fraction`, and `Path`.
    """

    def default(self, o: Any) -> Any:
        if isinstance(o, complex):
            return {
                _JSON_CUSTOM_TYPE_KEY: 'complex',
                _JSON_CUSTOM_TYPE_VALUE: str(o)
            }
        elif isinstance(o, Decimal):
            return {
                _JSON_CUSTOM_TYPE_KEY: 'Decimal',
                _JSON_CUSTOM_TYPE_VALUE: str(o)
            }
        elif isinstance(o, Fraction):
            return {
                _JSON_CUSTOM_TYPE_KEY: 'Fraction',
                _JSON_CUSTOM_TYPE_VALUE: str(o)
            }
        elif isinstance(o, Path):
            return {
                _JSON_CUSTOM_TYPE_KEY: 'Path',
                _JSON_CUSTOM_TYPE_VALUE: str(o)
            }
        return super().default(o)


def root_config_json_decode_object_hook(dct: dict[str, Any]):
    """Custom Python object hook for JSON decoder to decode non-standard types
    such as `complex`, `Decimal`, `Fraction`, and `Path`.
    """
    if (
        _JSON_CUSTOM_TYPE_KEY in dct and
        _JSON_CUSTOM_TYPE_VALUE in dct and
        len(dct) == 2
    ):
        key = dct[_JSON_CUSTOM_TYPE_KEY]
        value = dct[_JSON_CUSTOM_TYPE_VALUE]
        if key == 'complex':
            return complex(value)
        elif key == 'Decimal':
            return Decimal(value)
        elif key == 'Fraction':
            return Fraction(value)
        elif key == 'Path':
            return Path(value)
    return dct


@dataclass
class RootConfig(ABC):
    """The `RootConfig` class.

    A Python `dataclass` with special power,
    `RootConfig` can be extended to create your own configuration class
    for project variables management.

    For your own config class, remember to decorate the class with `@dataclass`

    ```python
    @dataclass
    class Config(RootConfig):
        epoch: int
        lr: float
    ```
    """

    @classmethod
    def from_dict(cls, dic: dict[str, Any]):
        """Create an instance from a `dict`.

        Keys from the input `dict` that does not exist in the class
        will be filtered.
        """

        names = {field.name for field in fields(cls)}
        filtered_dict = {k: v for k, v in dic.items() if k in names}
        return cls(**filtered_dict)

    @classmethod
    def from_json(cls, json_file: os.PathLike):
        """Create an instance from a JSON file.

        Also see `to_json` instance method.
        """

        with open(json_file, 'r') as f:
            incoming_data = json.load(
                f, object_hook=root_config_json_decode_object_hook
            )
        return cls.from_dict(incoming_data)

    @classmethod
    def parse_args(
        cls, arguments: list[str] | None = None,
        parser: ArgumentParser | None = None,
    ):
        """Create an instance from a Python `ArgumentParser`

        Without providing a list of arguments, `sys.argv[1:]` will be consumed.

        If no parser is provided, the default one forged from the class
        will be used. If one is provided, the provided parser would be
        directly utilized untouched. This is fundamentally different
        compared with `forge_parser` class method, as the latter would
        touch the provided parser.

        ```python
        config = Config.parse_args()
        ```
        """

        if parser is None:
            parser = cls.forge_parser(parser)
        args = parser.parse_args(arguments)
        return cls.from_dict(vars(args))

    @classmethod
    def forge_parser(
        cls, parser: ArgumentParser | None = None,
    ):
        """Forge a Python `ArgumentParser` to parse config arguments.

        If a parser is provided, this method would attach arguments
        to the given parser. Otherwise, a default parser of the class
        would be returned.
        """

        if parser is None:
            parser = ArgumentParser()
        for arg_name, arg_options in cls.parser_named_options():
            parser.add_argument(arg_name, **arg_options)
        return parser

    @classmethod
    def parser_named_options(cls):
        """Iterate through the class to create argument names and options
        for a Python `ArgumentParser` instance.

        All command-line arguments are keyword arguments.
        For those data class fields that do not have default values,
        those keyword arguments are not optional.

        This method is used when forging the default `ArgumentParser`
        for the class.

        ```python
        for name, options in config.parser_named_options():
            parser.add_argument(name, **options)
        ```
        """

        prefix_char = '-'
        for field in fields(cls):
            arg_name = prefix_char * 2 + field.name.replace('_', prefix_char)

            arg_options: dict[str, Any] = dict()
            arg_options['required'] = (
                field.default == MISSING and field.default_factory == MISSING
            )
            if field.default != MISSING or field.default_factory != MISSING:
                assert not arg_options['required']
                arg_options['default'] = (
                    field.default_factory()
                    if field.default_factory != MISSING else field.default
                )
            if get_origin(field.type) is list:
                list_type = get_args(field.type)[0]
                if list_type is bool:
                    arg_options['type'] = parse_bool
                else:
                    arg_options['type'] = list_type
                arg_options['nargs'] = '*'
            elif get_origin(field.type) is Literal:
                arg_options['type'] = type(get_args(field.type)[0])
                arg_options['choices'] = get_args(field.type)
            elif field.type is bool:
                arg_options['type'] = parse_bool
                arg_options['choices'] = [True, False]
            else:
                arg_options['type'] = field.type

            yield arg_name, arg_options

    def __post_init__(self):
        self.check_sanity()

    def to_dict(self):
        """Convert the instance to a Python `dict`."""

        return asdict(self)

    def to_json(self, json_file: os.PathLike):
        """Textualize the instance to a JSON file.

        Also see `from_json` class method.
        """

        with open(json_file, 'w') as f:
            json.dump(self.to_dict(), f, cls=RootConfigJSONEncoder)

    def check_sanity(self):
        """Validate whether the instance is a proper `RootConfig` instance.

        This method does two things: validate whether
        the instance is a valid Python `dataclass`, and
        validate whether all fields' type with there values
        are valid.
        """
        self._validate_instance_is_dataclass()
        self._validate_instance_variable_types()

    def _validate_instance_is_dataclass(self):
        if not is_dataclass(self):
            raise TypeError(
                f'`{self.__class__.__name__}` is not a Python `dataclass`. '
                f'Perhaps you forget to use `@dataclass` decorator?'
            )

    def _validate_instance_variable_types(self):
        for field in fields(self):
            field_name = field.name
            field_type = field.type

            try:
                field_val = getattr(self, field_name)
            except AttributeError:
                raise ValueError(
                    f'`{field_name}` expects a value, but nothing is provided.'
                )

            if field_type in supported_singleton_types:
                if not isinstance(field_val, field_type):
                    raise TypeError(
                        f'`{field_name}` is expected to be a(n) `{field_type}`'
                        f' but got {type(field_val)}.'
                    )
            elif get_origin(field_type) is Literal:
                literal_args = get_args(field_type)
                literal_types = list(map(type, get_args(field_type)))

                for literal_arg, literal_type in zip(
                    literal_args, literal_types
                ):
                    if literal_type not in supported_singleton_types:
                        raise TypeError(
                            f'Expectes all `Literal` value members to have '
                            f'type {supported_singleton_types}, '
                            f'but found {literal_arg} '
                            f'with type {literal_type}.'
                        )

                for (prev_arg, prev_type), (curr_arg, curr_type) in pairwise(
                    zip(literal_args, literal_types)
                ):
                    if prev_type is not curr_type:
                        raise TypeError(
                            f'Expects all choices in a `Literal` type to have '
                            f'the same type, but found inconsistent members '
                            f'`{prev_arg}` with type '
                            f'`{prev_type}` and '
                            f'`{curr_arg}` with type '
                            f'`{curr_type}`.'
                        )

                if field_val not in literal_args:
                    raise TypeError(
                        f'`{field_val}` is not one of `{literal_args}`.'
                    )
            elif get_origin(field_type) is list:
                list_args = get_args(field_type)
                if len(list_args) != 1:
                    raise TypeError(
                        f'Expect only one member type in list, '
                        f'but found {list_args}.'
                    )

                list_type = list_args[0]
                if list_type not in supported_singleton_types:
                    raise TypeError(
                        f'Expect the list to have one of '
                        f'`{supported_singleton_types}` type '
                        f'but found `{list_type}`.'
                    )

                if not isinstance(field_val, list):
                    raise TypeError(
                        f'`{field_name}` is expected to be a list, '
                        f'but got {type(field_val)}. '
                    )
                for v in field_val:
                    if not isinstance(v, list_type):
                        raise TypeError()
            else:
                raise TypeError(
                    f'`{field_type}` is not supported by `RootConfig`.'
                )
