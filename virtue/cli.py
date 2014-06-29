import argparse
import sys

from virtue import __version__, locators
from virtue.compat import unittest


parser = argparse.ArgumentParser(
    prog="virtue",
    description="virtue runs tests from any modules and objects specified",
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


def run(tests=()):
    locator = locators.ObjectLocator()
    cases = (
        case
        for test in tests
        for loader in locator.locate_by_name(test)
        for case in loader.load()
    )
    suite = unittest.TestSuite(cases)
    result = unittest.TestResult()
    suite.run(result)
    return result


def parse_args(args):
    return vars(parser.parse_args(args=args or ["--help"]))
