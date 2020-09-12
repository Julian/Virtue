import unittest
import warnings

import attr

from virtue.locators import ObjectLocator
from virtue.reporters import Counter


def run(tests=(), reporter=None, stop_after=None):
    """
    Run the tests that are loaded by each of the strings provided.

    Arguments:

        tests (collections.abc.Iterable):

            the collection of tests (specified as `str` s) to run

        reporter (twisted.trial.itrial.IReporter):

            a reporter to use for the run. If unprovided, the default is
            to return a `virtue.reporters.Counter` (which produces no
            output).

        stop_after (int):

            a number of non-successful tests to allow before stopping the run.
    """

    if reporter is None:
        reporter = Counter()
    if stop_after is not None:
        reporter = _StopAfterWrapper(reporter=reporter, limit=stop_after)

    locator = ObjectLocator()
    cases = (
        case
        for test in tests
        for loader in locator.locate_by_name(name=test)
        for case in loader.load()
    )
    suite = unittest.TestSuite(cases)
    getattr(reporter, "startTestRun", lambda: None)()
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        suite.run(reporter)
    getattr(reporter, "stopTestRun", lambda: None)()
    return reporter


@attr.s(eq=False)
class _StopAfterWrapper(object):
    """
    Wrap a reporter to stop after a specified number of non-successes.

    """

    _limit = attr.ib()
    _reporter = attr.ib()

    _seen = attr.ib(default=0)

    def __eq__(self, other):
        return self._reporter == other

    def __ne__(self, other):
        return not self == other

    def __getattr__(self, attr):
        return getattr(self._reporter, attr)

    def addError(self, *args, **kwargs):
        self._see_nonsuccess()
        self._reporter.addError(*args, **kwargs)

    def addFailure(self, *args, **kwargs):
        self._see_nonsuccess()
        self._reporter.addFailure(*args, **kwargs)

    def addUnexpectedSuccess(self, *args, **kwargs):
        self._see_nonsuccess()
        self._reporter.addUnexpectedSuccess(*args, **kwargs)

    def _see_nonsuccess(self):
        self._seen += 1
        if self._seen == self._limit:
            self.shouldStop = True
