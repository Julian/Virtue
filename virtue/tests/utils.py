from unittest import TestResult


class ExpectedResult(object):
    """
    A TestResult comparator.

    """

    def __init__(self, testsRun):
        self.testsRun = testsRun

    def __eq__(self, other):
        if not isinstance(other, TestResult):
            return NotImplemented
        return self.testsRun == other.testsRun

    def __ne__(self, other):
        return not self == other
