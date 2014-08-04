from virtue import locators
from virtue.compat import unittest


def run(tests=(), reporter=None):
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
    getattr(reporter, "startTestRun", lambda : None)()
    suite.run(reporter)
    getattr(reporter, "stopTestRun", lambda : None)()
    return reporter
