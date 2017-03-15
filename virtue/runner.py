from virtue import locators
from virtue.compat import unittest


def run(tests=(), reporter=None):
    """
    Run the tests that are loaded by each of the strings provided.

    Arguments:

        tests (iterable):

            the collection of tests (specified as `str` s) to run

        reporter (Reporter):

            a `Reporter` to use for the run. If unprovided, the default
            is to return a `unittest.TestResult` (which produces no
            output).

    """

    if reporter is None:
        reporter = unittest.TestResult()

    locator = locators.ObjectLocator()
    cases = (
        case
        for test in tests
        for loader in locator.locate_by_name(test)
        for case in loader.load()
    )
    suite = unittest.TestSuite(cases)
    getattr(reporter, "startTestRun", lambda: None)()
    suite.run(reporter)
    getattr(reporter, "stopTestRun", lambda: None)()
    return reporter
