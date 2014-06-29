from virtue import cli
from virtue.compat import unittest
from virtue.tests.utils import ExpectedResult


class TestRun(unittest.TestCase):
    def test_it_runs_tests(self):
        result = cli.run(tests=["virtue.tests.samples.one_successful_test"])
        self.assertEqual(result, ExpectedResult(testsRun=1))
