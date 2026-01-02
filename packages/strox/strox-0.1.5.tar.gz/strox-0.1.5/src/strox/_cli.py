from __future__ import annotations

import sys
import argparse

# Only *one* symbol will be available at runtime, hence the ignore
from argparse import ArgumentDefaultsHelpFormatter as Formatter  # type: ignore
from importlib.metadata import version

from . import Budget, get_closest_match

try:
    from rich_argparse import ArgumentDefaultsRichHelpFormatter

    class Formatter(ArgumentDefaultsRichHelpFormatter):
        styles = {
            "argparse.args": "bright_cyan",
            "argparse.groups": "bold underline bright_yellow",
            "argparse.help": "default",
            "argparse.metavar": "bold white",
            "argparse.syntax": "bold",
            "argparse.text": "bright_white",
            "argparse.prog": "bright_cyan",
            "argparse.default": "italic magenta",
        }

except ModuleNotFoundError:
    pass  # Using fallback symbol that is already imported as `Formatter`


class ParserArguments(argparse.Namespace):
    query: str
    options: list[str]
    substitution_cost: float
    insertion_cost: float
    deletion_cost: float
    equality_bonus: float
    start_bonus: float
    end_bonus: float


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="strox.exe",
        description="Command line interface for the `strox` package",
        add_help=False,
        formatter_class=Formatter,
    )
    parser.add_argument(
        "--substitution-cost",
        "-s",
        "--sub",
        type=float,
        metavar="FLOAT",
        default=Budget._field_defaults["substitution_cost"],
        help="Substitution cost",
    )
    parser.add_argument(
        "--insertion-cost",
        "-i",
        "--ins",
        type=float,
        metavar="FLOAT",
        default=Budget._field_defaults["insertion_cost"],
        help="Insertion cost",
    )
    parser.add_argument(
        "--deletion-cost",
        "-d",
        "--del",
        type=float,
        metavar="FLOAT",
        default=Budget._field_defaults["deletion_cost"],
        help="Deletion cost",
    )
    parser.add_argument(
        "--equality-bonus",
        "-e",
        "--eq",
        type=float,
        metavar="FLOAT",
        default=Budget._field_defaults["equality_bonus"],
        help="Equality bonus",
    )
    parser.add_argument(
        "--start-bonus",
        "--sb",
        type=float,
        metavar="FLOAT",
        default=Budget._field_defaults["start_bonus"],
        help="Start bonus",
    )
    parser.add_argument(
        "--end-bonus",
        "--eb",
        type=float,
        metavar="FLOAT",
        default=Budget._field_defaults["end_bonus"],
        help="End bonus",
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        help="Show this help message and exit",
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s: v{version('strox')}",
        help="Show `%(prog)s` version number and exit",
    )
    parser.add_argument(
        "query",
        type=str,
        metavar="<query>",
        help="Query to match against",
    )
    parser.add_argument(
        "options",
        nargs="+",
        type=list[str],
        metavar="<option>",
        help="Options to run query against",
    )

    args = ParserArguments()
    parser.parse_args(namespace=args)

    result = get_closest_match(
        args.query,
        args.options,
        budget=Budget(
            substitution_cost=args.substitution_cost,
            insertion_cost=args.insertion_cost,
            deletion_cost=args.deletion_cost,
            equality_bonus=args.equality_bonus,
            start_bonus=args.start_bonus,
            end_bonus=args.end_bonus,
        ),
    )
    sys.stdout.write(result)

    return 0
