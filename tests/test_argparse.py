from argparse import ArgumentError
from dataclasses import dataclass, field
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Literal
from unittest import TestCase

from rootconfig import RootConfig


@dataclass
class Config(RootConfig):
    batch_size: int
    lpf_pole: complex
    learning_rates: list[Decimal]
    optimizer: Literal['Adam', 'AdamW', 'RMSProp']
    debug: bool = False
    random_seed: int = 1
    model_version: Literal[1, 2, 3] = 2
    dataset_path: Path = Path.cwd() / 'datasets'
    ratios: list[Fraction] = field(
        default_factory=lambda: [Fraction(1, 3)]
    )


class ArgumentParsingTest(TestCase):
    def test_argument_parser_options_name(self):
        arg_names = [
            arg_name for arg_name, _ in
            Config.parser_named_options()
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
        for arg_name, arg_options in Config.parser_named_options():
            self.assertIn(
                'type', arg_options,
                'All arguments should have its `type` specified.'
            )

            if arg_name == '--lpf-pole':
                count += 1
                self.assertIs(
                    arg_options['type'], complex,
                    'Should have correct types.'
                )
            elif arg_name == '--random-seed':
                count += 1
                self.assertIs(
                    arg_options['type'], int,
                    'Should have correct types.'
                )
                self.assertEqual(
                    arg_options['default'], 1,
                    'Should have correct default values.'
                )
            elif arg_name == '--ratios':
                count += 1
                self.assertIs(
                    arg_options['type'], Fraction,
                    'Should have correct types.'
                )
                self.assertEqual(
                    arg_options['default'], [Fraction('1/3')],
                    'Should have correct default values.'
                )
            elif arg_name == '--model-version':
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
            elif arg_name == '--optimizer':
                count += 1
                self.assertIs(
                    arg_options['type'], str,
                    'Should have correct types.'
                )
                self.assertEqual(
                    arg_options['choices'], ('Adam', 'AdamW', 'RMSProp'),
                    'Should have correct default values.'
                )
                self.assertNotIn(
                    'default', arg_options,
                    'Should not have default value if there is no one.'
                )

        self.assertEqual(count, 5, 'Should have correct argument names.')

    def test_parse_arguments(self):
        with self.assertRaises(
            SystemExit, msg='Should exit if no arguments are provided.'
        ):
            config = Config.parse_args([])

        with self.assertRaises(
            SystemExit, msg='Should exit if some arguments are missing.'
        ):
            config = Config.parse_args([
                '--batch-size', '128', '--lpf-pole', '0+1j',
                '--learning-rates', '0.1',  # '--optimizer', 'Adam',
            ])

        with self.assertRaises(
            SystemExit, msg='Should exit if not using correct notations.'
        ):
            config = Config.parse_args([
                '--batch_size', '128', '--lpf-pole', '0+1j',
                '--learning-rates', '0.1',  # '--optimizer', 'Adam',
            ])

        with self.assertRaises(
            SystemExit, msg='Should exit if some arguments are incorrect.'
        ):
            config = Config.parse_args([
                '--batch-size', '128', '--lpf-pole', '0+1j',
                '--learning-rates', '0.1', '--optimizer', 'SGD',
            ])

        with self.assertRaises(
            SystemExit,
            msg='Should exit if some arguments cannot be converted.'
        ):
            config = Config.parse_args([
                '--batch-size', '0+0j', '--lpf-pole', '0+1j',
                '--learning-rates', '0.1', '--optimizer', 'Adam',
            ])

        with self.assertRaises(
            SystemExit,
            msg='Should exit if some values are missing.'
        ):
            config = Config.parse_args([
                '--batch-size', '--lpf-pole', '0+1j',
                '--learning-rates', '0.1', '--optimizer', 'Adam',
            ])

        with self.assertRaises(
            SystemExit,
            msg='Should exit if boolean is not properly supplied.'
        ):
            config = Config.parse_args([
                '--batch-size', '128', '--lpf-pole', '0+1j',
                '--learning-rates', '0.1', '--optimizer', 'Adam',
                '--debug', 'FFalse'
            ])

        with self.assertRaises(
            SystemExit,
            msg='Should exit if an argument with a default value'
                'is about to receive value but nothing is provided.'
        ):
            config = Config.parse_args([
                '--batch-size', '128', '--lpf-pole', '0+1j',
                '--learning-rates', '0.1', '--optimizer', 'Adam',
                '--debug',
            ])

        with self.assertRaises(
            SystemExit,
            msg='Should exit if a list contains invalid value.'
        ):
            config = Config.parse_args([
                '--batch-size', '128', '--lpf-pole', '0+1j',
                '--learning-rates', '0.1', '--optimizer', 'Adam',
                '--ratios', '3/4', 'inf'
            ])

        with self.assertRaises(
            SystemExit,
            msg='Should exit if invalid arguments is provided.'
        ):
            config = Config.parse_args([
                '--batch-size', '128', '--lpf-pole', '0+1j',
                '--learning-rates', '0.1', '--optimizer', 'Adam',
                '--i-am-an-imposter', 'whatever',
            ])

        with self.assertRaises(
            SystemExit,
            msg='Should exit if invalid arguments is provided.'
        ):
            config = Config.parse_args([
                '--batch-size', '128', '--lpf-pole', '0+1j',
                '--learning-rates', '0.1', '--optimizer', 'Adam',
                'whatever',
            ])

        config = Config.parse_args([
            '--batch-size', '128', '--lpf-pole', '0+1j',
            '--learning-rates', '--optimizer', 'Adam',
        ])
        self.assertEqual(
            config.batch_size, 128,
            'Should correctly parse value.'
        )
        self.assertEqual(
            config.lpf_pole, 1j,
            'Should correctly parse value.'
        )
        self.assertEqual(
            config.optimizer, 'Adam',
            'Should correctly parse value.'
        )
        self.assertEqual(
            len(config.learning_rates), 0,
            '`list` can have no values.'
        )
        self.assertEqual(
            config.debug, False,
            'Default values should be preserved.'
        )
        self.assertEqual(
            config.model_version, 2,
            'Default values should be preserved.'
        )
        self.assertEqual(
            config.dataset_path, Path.cwd() / 'datasets',
            'Default values should be preserved.'
        )
        self.assertEqual(
            config.ratios, [Fraction('1/3')],
            'Default values should be preserved.'
        )

        config = Config.parse_args([
            '--batch-size', '128', '--lpf-pole', '0+1j',
            '--learning-rates', '1e-2', '1e-3', '1e-4',
            '--optimizer', 'Adam',
            '--debug', 'True', '--random-seed', '3',
            '--model-version', '1', '--dataset-path', '/bin',
            '--ratios', '2/3', '3/3', '10/3',
        ])
        self.assertListEqual(
            config.learning_rates,
            [Decimal('1e-2'), Decimal('1e-3'), Decimal('1e-4')],
            'Should properly parse a list of values.'
        )
        self.assertEqual(
            config.debug, True,
            'Provided values should override default values.'
        )
        self.assertEqual(
            config.random_seed, 3,
            'Provided values should override default values.'
        )
        self.assertEqual(
            config.dataset_path, Path('/bin'),
            'Provided values should override default values.'
        )
        self.assertListEqual(
            config.ratios, [Fraction(2, 3), Fraction(3, 3), Fraction(10, 3)],
            'Provided values should override default values, '
            'including `lists.'
        )
        self.assertNotIn(
            Fraction('1/3'), config.ratios,
            'Provided values should override default values, '
            'including `lists.'
        )
