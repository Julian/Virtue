import argparse
import sys

from twisted.python.reflect import namedAny as named_any

# Sigh. http://twistedmatrix.com/trac/ticket/8267
import twisted.trial.unittest

import twisted.trial.reporter

from virtue import __version__
from virtue.reporters import ComponentizedReporter
from virtue.runner import run


_BUILT_IN_REPORTERS = {
    "bwverbose": twisted.trial.reporter.VerboseTextReporter,
    "default": ComponentizedReporter,
    "subunit": twisted.trial.reporter.SubunitReporter,
    "summary": twisted.trial.reporter.MinimalReporter,
    "text": twisted.trial.reporter.TextReporter,
    "timing": twisted.trial.reporter.TimingTextReporter,
    "tree": twisted.trial.reporter.TreeReporter,
    "verbose": twisted.trial.reporter.VerboseTextReporter,
}


def _reporter_by_name(name):
    Reporter = _BUILT_IN_REPORTERS.get(name)
    if Reporter is not None:
        return Reporter()

    try:
        return named_any(name)
    except Exception:
        message = "{0!r} is not a known reporter".format(name)
        raise argparse.ArgumentTypeError(message)


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
    "--reporter",
    default=ComponentizedReporter(),
    help="the name of a reporter to use for outputting test results",
    type=_reporter_by_name,
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
