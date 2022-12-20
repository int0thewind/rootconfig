from argparse import ArgumentParser
from dataclasses import KW_ONLY, dataclass, field
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Literal
from unittest import TestCase

from base_config import BaseConfig


@dataclass
class Config(BaseConfig):
    epochs: int
    learning_rates: list[Decimal]
    lpf_pole: complex
    epsilon: float
    optimizer: Literal['Adam', 'AdamW', 'RMSProp']
    model_version: Literal[1, 2, 3] = 2
    random_seed: int = 1

    _: KW_ONLY
    batch_size: int
    debug: bool = False
    dataset_path: Path = Path.cwd() / 'datasets'
    ratios: list[Fraction] = field(
        default_factory=lambda: [Fraction(1, 3)]
    )


class ArgumentParsingTest(TestCase):
    def test_argument_parser_options_name(self):
        arg_names = [
            arg_name for arg_name, _ in
            Config.argument_parser_named_options()
        ]
        for arg_name in arg_names:
            self.assertEqual(
                arg_name[:2], '--', 'All arguments must be keyword arguments.'
            )
        self.assertIn(
            '--dataset-path', arg_names,
            'Keyword-only fields with underscores should'
            'have its underscores converted to hyphens.'
        )
        self.assertNotIn(
            '--batch_size', arg_names,
            'Keyword-only fields should have all its underscores '
            'converted to hyphens when being converted to CLI arguments.'
        )

    def test_argument_parser_options(self):
        count = 0
        for arg_name, arg_options in Config.argument_parser_named_options():
            self.assertIn(
                'type', arg_options,
                'All arguments should have its `type` specified.'
            )
            self.assertIn(
                'required', arg_options,
                'All arguments should have its `required` specified.'
            )
            if arg_name == '--epsilon':
                count += 1
                self.assertIs(
                    arg_options['type'], float,
                    'Should have correct types.'
                )
            if arg_name == '--random-seed':
                count += 1
                self.assertIs(
                    arg_options['type'], int,
                    'Should have correct types.'
                )
                self.assertEqual(
                    arg_options['default'], 1,
                    'Should have correct default values.'
                )
            if arg_name == '--ratios':
                count += 1
                self.assertIs(
                    arg_options['type'], Fraction,
                    'Should have correct types.'
                )
                self.assertEqual(
                    arg_options['default'], [Fraction('1/3')],
                    'Should have correct default values.'
                )
            if arg_name == '--model-version':
                count += 1
                self.assertIs(
                    arg_options['type'], int,
                    'Should have correct types.'
                )
                self.assertEqual(
                    arg_options['default'], 2,
                    'Should have correct default values.'
                )
                self.assertEqual(
                    arg_options['choices'], (1, 2, 3),
                    'Should have correct default values.'
                )
            if arg_name == '--optimizer':
                count += 1
                self.assertIs(
                    arg_options['type'], str,
                    'Should have correct types.'
                )
                self.assertEqual(
                    arg_options['choices'], ('Adam', 'AdamW', 'RMSProp'),
                    'Should have correct default values.'
                )

        self.assertEqual(count, 5, 'Should have correct argument names.')
