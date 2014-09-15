from difflib import ndiff
from textwrap import dedent

from virtue import runner
from virtue.reporters import ComponentizedReporter, Outputter
from virtue.compat import StringIO, unittest
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


class TestRunOutput(unittest.TestCase):
    def assertOutputIs(self, expected, **kwargs):
        reporter = ComponentizedReporter(
            outputter=Outputter(colored=False, line_width=40),
            stream=StringIO(),
            time=lambda : 0,
        )
        runner.run(reporter=reporter, **kwargs)
        got = reporter.stream.getvalue()

        dedented = dedent(expected)
        if dedented.startswith("\n"):
            dedented = dedented[1:]

        if got != dedented:
            self.fail(
                "\n    " +
                "\n    ".join(ndiff(got.splitlines(), dedented.splitlines()))
            )

    def test_empty_run(self):
        self.assertOutputIs(
            tests=[],
            expected="""

            ----------------------------------------
            Ran 0 tests in 0.000s

            PASSED
            """
        )
