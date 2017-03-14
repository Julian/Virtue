import attr


@attr.s(cmp=False)
class ExpectedResult(object):
    """
    A TestResult comparator.

    """

    errors = attr.ib(default=0)
    failures = attr.ib(default=0)
    testsRun = attr.ib(default=0)

    def __eq__(self, other):
        return (
            self.errors == len(other.errors) and
            self.failures == len(other.failures) and
            self.testsRun == other.testsRun
        )

    def __ne__(self, other):
        return not self == other
