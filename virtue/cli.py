from virtue import locators
from virtue.compat import unittest


def main():
    pass


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
