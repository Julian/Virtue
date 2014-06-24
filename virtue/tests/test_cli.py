from virtue import cli
from virtue.compat import unittest


class TestRun(unittest.TestCase):
    def test_it_runs_tests(self):
        result = cli.run(tests=["virtue.tests.samples.successful"])
        self.assertTrue(result.wasSuccessful())
