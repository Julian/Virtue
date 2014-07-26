from virtue import runner
from virtue.compat import unittest
from virtue.tests.utils import ExpectedResult


class TestRun(unittest.TestCase):
    def test_it_runs_tests(self):
        result = runner.run(tests=["virtue.tests.samples.one_successful_test"])
        self.assertEqual(result, ExpectedResult(testsRun=1))

    def test_it_allows_specifying_a_result(self):
        result = unittest.TestResult()
        runner.run(
            tests=["virtue.tests.samples.one_successful_test"],
            reporter=result,
        )
        self.assertEqual(result, ExpectedResult(testsRun=1))
