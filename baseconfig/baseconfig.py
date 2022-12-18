import os
import json
import sys
from abc import ABC
from argparse import ArgumentParser
from dataclasses import asdict, dataclass, fields
from decimal import Decimal
from fractions import Fraction
from numbers import Complex, Integral, Number, Rational, Real
from typing import Any, Union, Literal, get_args, get_origin, get_type_hints

__all__ = ['BaseConfig']

_supported_numerical_types = [
    int, Fraction, Decimal, float, complex,
    Number, Complex, Real, Rational, Integral,
]

_supported_types = [
    str, dict, list, Union, Literal, Any,
] + _supported_numerical_types


@dataclass(init=True, eq=False, repr=False)
class BaseConfig(ABC):
    @classmethod
    def validate_types(cls, incoming_data: dict[str, Any]):
        pass

    @classmethod
    def from_dict(cls, from_dict: dict[str, Any]):
        cls.validate_types(from_dict)
        return cls(**from_dict)

    @classmethod
    def from_json(
        cls, json_file: os.PathLike, *,
        enable_complex: bool = True,
        enable_decimal: bool = True,
        enable_fraction: bool = True,
    ):
        with open(json_file, 'r') as f:
            incoming_data = json.load(f)
        cls.validate_types(incoming_data)
        return cls(**incoming_data)

    @classmethod
    def from_program_arguments(cls, arguments: list[str] | None):
        if arguments is None:
            arguments = sys.argv[1:]
        raise NotImplementedError

    @classmethod
    def forge_argument_parser(cls, *, parser: ArgumentParser | None):
        if parser is None:
            parser = ArgumentParser()
        raise NotImplementedError

    def to_dict(self):
        return asdict(self)

    def to_json(
        self, json_file: os.PathLike, *,
        enable_complex: bool = True,
        enable_decimal: bool = True,
        enable_fraction: bool = True,
    ):
        with open(json_file, 'w') as f:
            json.dump(self.to_dict(), f)

    def validate_instance_variable_types(self):
        for field_def in fields(self):
            field_type = field_def.type
            field_name = field_def.name
            field_value = getattr(self, field_name)

            # if isinstance(field_def.type, typing._SpecialForm):
            #     # No check for typing.Any, typing.Union, typing.ClassVar (without parameters)
            #     continue
            # try:
            #     actual_type = field_def.type.__origin__
            # except AttributeError:
            #     # In case of non-typing types (such as <class 'int'>, for instance)
            #     actual_type = field_def.type
            #     # In Python 3.8 one would replace the try/except with
            #     # actual_type = typing.get_origin(field_def.type) or field_def.type
            # if isinstance(actual_type, typing._SpecialForm):
            #     # case of typing.Union[…] or typing.ClassVar[…]
            #     actual_type = field_def.type.__args__

            # actual_value = getattr(self, field_name)
            # if not isinstance(actual_value, actual_type):
            #     print(f"\t{field_name}: '{type(actual_value)}' instead of '{field_def.type}'")
            #     ret = False
