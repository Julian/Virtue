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

    def test_unsuccessful_run(self):
        from virtue.tests.samples import two_unsuccessful_tests
        self.assertOutputIs(
            tests=[
                "virtue.tests.samples.one_successful_test",
                "virtue.tests.samples.two_unsuccessful_tests",
            ],
            expected="""
            virtue.tests.samples.one_successful_test
              Foo
                test_foo ...                    [OK]
            virtue.tests.samples.two_unsuccessful_tests
              Bar
                test_bar ...                    [OK]
                test_foo ...                  [FAIL]
              Foo
                test_bar ...                  [FAIL]
                test_foo ...                    [OK]

            ========================================
            [FAIL]
            Traceback (most recent call last):
              File "{unittest.case.__file__}", line 329, in run
                testMethod()
              File "{two_unsuccessful_tests.__file__}", line 14, in test_foo
                self.fail("I fail too.")
              File "{unittest.case.__file__}", line 410, in fail
                raise self.failureException(msg)
            AssertionError: I fail too.

            virtue.tests.samples.two_unsuccessful_tests.Bar.test_foo
            ========================================
            [FAIL]
            Traceback (most recent call last):
              File "{unittest.case.__file__}", line 329, in run
                testMethod()
              File "{two_unsuccessful_tests.__file__}", line 9, in test_bar
                self.fail("I fail.")
              File "{unittest.case.__file__}", line 410, in fail
                raise self.failureException(msg)
            AssertionError: I fail.

            virtue.tests.samples.two_unsuccessful_tests.Foo.test_bar
            ----------------------------------------
            Ran 5 tests in 0.000s

            FAILED (successes=3, failures=2)
            """.format(
                unittest=unittest,
                two_unsuccessful_tests=two_unsuccessful_tests,
            )
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
