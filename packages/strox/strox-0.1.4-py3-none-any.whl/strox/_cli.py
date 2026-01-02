import argparse
import sys
from importlib.metadata import version

from . import Budget, get_closest_match


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
        prog="strox",
        description="Command line interface for the `strox` package",
        add_help=False,
    )
    parser.add_argument(
        "--substitution-cost",
        "-s",
        "--sub",
        type=float,
        default=Budget._field_defaults["substitution_cost"],
        help="Substitution cost",
        metavar="FLOAT",
    )
    parser.add_argument(
        "--insertion-cost",
        "-i",
        "--ins",
        type=float,
        default=Budget._field_defaults["insertion_cost"],
        help="Insertion cost",
        metavar="FLOAT",
    )
    parser.add_argument(
        "--deletion-cost",
        "-d",
        "--del",
        type=float,
        default=Budget._field_defaults["deletion_cost"],
        help="Deletion cost",
        metavar="FLOAT",
    )
    parser.add_argument(
        "--equality-bonus",
        "-e",
        "--eq",
        type=float,
        default=Budget._field_defaults["equality_bonus"],
        help="Equality bonus",
        metavar="FLOAT",
    )
    parser.add_argument(
        "--start-bonus",
        "--sb",
        type=float,
        default=Budget._field_defaults["start_bonus"],
        help="Start bonus",
        metavar="FLOAT",
    )
    parser.add_argument(
        "--end-bonus",
        "--eb",
        type=float,
        default=Budget._field_defaults["end_bonus"],
        help="End bonus",
        metavar="FLOAT",
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
        help="Query to match against",
    )
    parser.add_argument(
        "options",
        nargs="+",
        help="Options to select from",
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
