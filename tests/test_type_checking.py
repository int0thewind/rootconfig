import math
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Literal, Union
from unittest import TestCase
from decimal import Decimal

from rootconfig import RootConfig


class TypeCheckingTest(TestCase):
    def test_singleton_type(self):
        @dataclass
        class Config(RootConfig):
            epsilon: float
            learning_rate: Decimal
            data_path: Path
            wandb: bool
            nan_val: float
            decimal_inf: Decimal

        config = Config(
            1e-8, Decimal('1e-4'), Path.cwd(), False,
            float('nan'), Decimal('inf')
        )
        self.assertEqual(
            config.learning_rate, Decimal('0.0001'),
            'Should correctly receive a value.'
        )
        self.assertEqual(
            type(config.epsilon), float,
            'Should correctly stores a value\'s type.'
        )
        self.assertTrue(
            math.isnan(config.nan_val),
            'Should correctly handle not-a-number value.'
        )
        self.assertTrue(
            Decimal.is_infinite(config.decimal_inf),
            'Should correctly handle infinite value.'
        )

    def test_singleton_type_exception(self):
        with self.assertRaises(
            TypeError, msg='Should not have unsupported types.',
        ):
            @dataclass
            class Config1(RootConfig):
                attr1: bytes
            Config1(b'abc')

        with self.assertRaises(
            TypeError, msg='Should catch value with incorrect type.',
        ):
            @dataclass
            class Config2(RootConfig):
                attr1: str
            Config2(b'abc')

        with self.assertRaises(
            TypeError, msg='Should catch malformed type.',
        ):
            @dataclass
            class Config3(RootConfig):
                attr1: '3'
            Config3(b'abc')

        with self.assertRaises(
            TypeError, msg='Should catch default value with incorrect type.',
        ):
            @dataclass
            class Config4(RootConfig):
                attr1: str = 3
            Config4()

    def test_literal_type(self):
        @dataclass
        class Config(RootConfig):
            criterion: Literal['mse', 'cos-face', 'ge2e']
            model_version: Literal[1, 2, 3, 4, 5, 0]

        config = Config('mse', 3)
        self.assertEqual(
            config.criterion, 'mse',
            'The class must be able to receive correct value.'
        )
        self.assertNotEqual(
            config.criterion, 3,
            'The class should not mess up received field value.'
        )
        self.assertEqual(
            config.model_version, 3,
            'The class must be able to receive correct value.'
        )
        self.assertNotEqual(
            config.model_version, 'mse',
            'The class should not mess up received field value.'
        )

    def test_literal_type_exception(self):
        with self.assertRaises(
            TypeError, msg='`Literal` type should have same value type.'
        ):
            @dataclass
            class Config1(RootConfig):
                model_version: Literal[1, 2, '3']
            Config1(2)

        with self.assertRaises(
            TypeError, msg='`Should catch erroneous default `Literal` value.'
        ):
            @dataclass
            class Config2(RootConfig):
                model_version: Literal[1, 2, 3, 4] = 0
            Config2()

        with self.assertRaises(
            TypeError, msg='Should detect not defined `Literal` values'
        ):
            @dataclass
            class Config3(RootConfig):
                model_version: Literal[1, 2, 3]
            Config3(4)

        with self.assertRaises(
            TypeError, msg='A bare `Literal` should not pass.'
        ):
            @dataclass
            class Config4(RootConfig):
                model_version: Literal
            Config4(100)

        with self.assertRaises(
            TypeError, msg='`Literal` should only contain supported types.'
        ):
            @dataclass
            class Config5(RootConfig):
                model_version: Literal[None]
            Config5(None)

    def test_list_type(self):
        @dataclass
        class Config(RootConfig):
            learning_rate_order: list[Decimal]
            poles: list[complex]
            log_files: list[Path]

        config = Config(
            [Decimal('1e-2'), Decimal('0.00001')],
            [1 + 0j, 0 + 1j, -1 + 0j],
            []
        )
        self.assertIs(
            type(config.poles), list,
            'The value of a field with `list` type must be a list.'
        )
        self.assertEqual(
            config.learning_rate_order[1], Decimal('1e-5'),
            'A `list` field should accept a list with its order.'
        )
        self.assertEqual(
            len(config.log_files), 0,
            '`RootConfig` class must be able to accept an empty list.'
        )

    def test_list_type_exception(self):
        with self.assertRaises(
            TypeError, msg='Cannot have more than one types in list.',
        ):
            @dataclass
            class Config(RootConfig):
                attr1: list[int, str]
            Config([1, 2, '3'])

        with self.assertRaises(
            TypeError, msg='Cannot have `Union` types in list.',
        ):
            @dataclass
            class Config2(RootConfig):
                attr1: list[int | str]
            Config2([1, 2, '3'])

        with self.assertRaises(
            TypeError, msg='Cannot have `Union` types in list.',
        ):
            @dataclass
            class Config3(RootConfig):
                attr1: list[Union[int, str]]
            Config3([1, 2, '3'])

        with self.assertRaises(
            TypeError, msg='Cannot have `Literal` types in list.'
        ):
            @dataclass
            class Config4(RootConfig):
                attr1: list[Literal['a', 'b', 'c']]
            Config4(['a', 'a', 'b'])

        with self.assertRaises(
            TypeError, msg='Cannot have `list` types in list.'
        ):
            @dataclass
            class Config5(RootConfig):
                attr1: list[list[str]]
            Config5([['a', 'a', 'b']])

        with self.assertRaises(
            TypeError, msg='Cannot have not supported singleton types in list.'
        ):
            @dataclass
            class Config6(RootConfig):
                attr1: list[None]
            Config6([None, None, None])

        with self.assertRaises(
            TypeError, msg='All elements in a list should match the type.',
        ):
            @dataclass
            class Config7(RootConfig):
                attr1: list[Fraction]
            Config7([1 / 2, Fraction('1/2')])

        with self.assertRaises(
            TypeError, msg='All elements in a list should match the type.'
        ):
            @dataclass
            class Config8(RootConfig):
                attr1: list[float]
            Config8([1, 2., 0.3])

        with self.assertRaises(
            TypeError, msg='A bare `list` type should not be accepted.'
        ):
            @dataclass
            class Config9(RootConfig):
                attr1: list
            Config9([1, 2., 0.3])

        with self.assertRaises(
            TypeError, msg='All elements in a list should match the type.',
        ):
            @dataclass
            class Config10(RootConfig):
                attr1: list[int] = field(
                    default_factory=lambda: [1, 2.0, 3]
                )
            Config10()

        with self.assertRaises(
            TypeError, msg='`list` field type should receive a list.',
        ):
            @dataclass
            class Config11(RootConfig):
                attr1: list[int] = field(
                    default_factory=lambda: (1, 2.0, 3)
                )
            Config11()
