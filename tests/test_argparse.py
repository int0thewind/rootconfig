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
        print(arg_names)

        self.assertNotIn(
            '--epoch', arg_names,
            'Positional-only singleton fields '
            'should not be keyword CLI arguments.'
        )
        self.assertNotIn(
            'lpf-pole', arg_names,
            'Positional-only singleton fields should not '
            'have its underscores converted to hyphens '
            'when being converted to CLI arguments. '
        )
        self.assertNotIn(
            'batch_size', arg_names,
            'Keyword-only fields should not be '
            'a positional-only CLI arguments.'
        )
        self.assertNotIn(
            '--batch_size', arg_names,
            'Keyword-only fields should have all its underscores '
            'converted to hyphens when being converted to CLI arguments.'
        )
        self.assertNotIn(
            'learning-rates', arg_names,
            'Positional-only list fields should be treated '
            'as keyword-only CLI arguments.'
        )

        self.assertIn(
            'epsilon', arg_names,
            'Positonal-only singleton fields '
            'should be treated as positional CLI arguments.'
        )
        self.assertIn(
            'lpf_pole', arg_names,
            'Positional-only singleton fields with underscores '
            'should keep its underscores.'
        )
        self.assertIn(
            '--debug', arg_names,
            'Keyword-only singleton fields '
            'should be treated as keyword CLI arguments.'
        )
        self.assertIn(
            '--dataset-path', arg_names,
            'Keyword-only fields with underscores should'
            'have its underscores converted to hyphens.'
        )
        self.assertIn(
            '--learning-rates', arg_names,
            'Positional-only list fields shoudl be treated as '
            'keyword CLI arguments.'
        )

    def test_argument_parser_options(self):
        for arg_name, arg_options in Config.argument_parser_named_options():
            self.assertIn(
                'type', arg_options,
                'All arguments should have its type specified.'
            )
            if arg_name == 'epochs':
