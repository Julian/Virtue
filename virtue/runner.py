import attr

from virtue.compat import unittest
from virtue.locators import ObjectLocator


def run(tests=(), reporter=None, stop_after=None):
    """
    Run the tests that are loaded by each of the strings provided.

    Arguments:

        tests (iterable):

            the collection of tests (specified as `str` s) to run

        reporter (Reporter):

            a `Reporter` to use for the run. If unprovided, the default
            is to return a `unittest.TestResult` (which produces no
            output).

        stop_after (int):

            a number of non-successful tests to allow before stopping the run.

    """

    if reporter is None:
        reporter = unittest.TestResult()
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
    suite.run(reporter)
    getattr(reporter, "stopTestRun", lambda: None)()
    return reporter


@attr.s
class _StopAfterWrapper(object):
    """
    Wrap a reporter to stop after a specified number of non-successes.

    """

    _limit = attr.ib()
    _reporter = attr.ib()

    _seen = attr.ib(default=0)

    def addError(self, *args, **kwargs):
        self._see_failure()
        self._reporter.addError(*args, **kwargs)

    def addFailure(self, *args, **kwargs):
        self._see_failure()
        self._reporter.addFailure(*args, **kwargs)

    def _see_failure(self):
        self._seen += 1
        if self._seen == self._limit:
            self.shouldStop = True

    def __getattr__(self, attr):
        return getattr(self._reporter, attr)
