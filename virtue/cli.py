import argparse
import sys

from virtue import __version__
from virtue.runner import run


parser = argparse.ArgumentParser(
    prog="virtue",
    description="virtue discovers and runs tests found in the given objects",
)
parser.add_argument(
    "-V", "--version",
    action="version",
    version=__version__,
)
parser.add_argument(
    "tests",
    help="one or more tests (packages, modules or objects) to run",
    nargs="+",
)


def main(args=sys.argv[1:]):
    result = run(**parse_args(args=args))
    sys.exit(not result.wasSuccessful())


def parse_args(args):
    return vars(parser.parse_args(args=args or ["--help"]))
