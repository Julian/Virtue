from difflib import ndiff
from io import StringIO
from textwrap import dedent
import os
import re
import unittest

from pyrsistent import v

from virtue import runner
from virtue.reporters import (
    ComponentizedReporter,
    Counter,
    Outputter,
    Recorder,
)


class TestRun(unittest.TestCase):
    def test_it_runs_tests(self):
        result = runner.run(tests=["virtue.tests.samples.one_successful_test"])
        self.assertEqual(result, Counter(successes=1))

    def test_it_runs_unsuccessful_tests(self):
        result = runner.run(
            tests=["virtue.tests.samples.one_unsuccessful_test"],
        )
        self.assertEqual(result, Counter(failures=1))

    def test_it_runs_expected_failing_tests(self):
        result = runner.run(
            tests=["virtue.tests.samples.one_expected_failure"],
        )
        self.assertEqual(result, Counter(expected_failures=1))

    def test_it_runs_unexpectedly_passing_expected_failing_tests(self):
        result = runner.run(
            tests=[
                "virtue.tests.samples.one_expected_failure_mispassing",
            ],
        )
        self.assertEqual(result, Counter(unexpected_successes=1))

    def test_it_runs_subtests(self):
        result = runner.run(tests=["virtue.tests.samples.subtests"])
        self.assertEqual(
            result,
            Counter(
                subtest_failures=1,
                subtest_successes=4,
                successes=3,
                errors=1,
            ),
        )

    def test_it_can_stop_short(self):
        """
        Ooo, I stopped short.
        """

        result = runner.run(
            tests=["virtue.tests.samples.two_unsuccessful_tests"],
            stop_after=1,
        )
        self.assertEqual(
            result,
            Counter(failures=1, successes=result.successes),
        )

    def test_it_can_stop_short_combined_with_errors(self):
        counter = runner.run(
            tests=["virtue.tests.samples.failures_and_errors"],
        )
        self.assertGreater(counter.failures + counter.errors, 3)

        result = runner.run(
            tests=["virtue.tests.samples.failures_and_errors"],
            stop_after=3,
        )
        self.assertEqual(result.failures + result.errors, 3)

    def test_it_can_stop_short_combined_with_unexpected_passing_tests(self):
        """
        RIP Jerry.
        """
        counter = runner.run(
            tests=["virtue.tests.samples.failures_and_unexpected_passes"],
        )
        self.assertGreater(counter.failures + counter.unexpected_successes, 2)

        result = runner.run(
            tests=["virtue.tests.samples.failures_and_unexpected_passes"],
            stop_after=2,
        )
        self.assertEqual(result.failures + result.unexpected_successes, 2)

    def test_warnings_become_errors_by_default(self):
        result = runner.run(
            tests=["virtue.tests.samples.success_and_warning"],
        )
        self.assertEqual(result, Counter(errors=1, successes=1))

    def test_it_runs_tests_by_path_if_you_insist(self):
        import virtue.tests.samples

        path = os.path.join(
            os.path.dirname(virtue.tests.samples.__file__),
            "one_unsuccessful_test.py",
        )
        result = runner.run(tests=[path])
        self.assertEqual(result, Counter(failures=1))

    def test_it_errors_for_paths_that_do_not_exist(self):
        path = os.path.join(
            os.path.dirname(__file__),
            "this_is_a_path_that_doesnt_exist_yes_it_goes_on_and_on_my_friend",
        )
        with self.assertRaises(FileNotFoundError):
            runner.run(tests=[path])

    def test_unittest_TestResult(self):
        result = unittest.TestResult()
        runner.run(
            tests=["virtue.tests.samples.one_successful_test"],
            reporter=result,
        )
        self.assertEqual(result.testsRun, 1)

    def test_Recorder(self):
        result = Recorder()
        runner.run(
            tests=["virtue.tests.samples.one_successful_test"],
            reporter=result,
        )
        import virtue.tests.samples.one_successful_test

        self.assertEqual(
            result,
            Recorder(
                successes=v(
                    virtue.tests.samples.one_successful_test.Foo("test_foo"),
                ),
            ),
        )


class TestRunOutput(unittest.TestCase):
    def assertOutputIs(self, expected, **kwargs):
        reporter = ComponentizedReporter(
            outputter=Outputter(colored=False, line_width=40),
            stream=StringIO(),
            time=lambda: 0,
        )
        runner.run(reporter=reporter, **kwargs)
        got = reporter.stream.getvalue()

        dedented = dedent(expected)
        if dedented.startswith("\n"):
            dedented = dedented[1:]

        # I'm so sorry.
        globbed = re.escape(dedented).replace(re.escape("•"), ".*")

        if re.search(globbed, got, re.DOTALL) is None:
            self.fail(
                "\n    "
                + "\n    ".join(
                    ndiff(got.splitlines(), dedented.splitlines()),
                ),
            )

    def test_unsuccessful_run(self):
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
            Traceback (most recent call last):•
              File "•unittest/case.py•", line •, in •
                •
              File "•virtue/tests/samples/two_unsuccessful_tests.py•", line 14, in test_foo
                self.fail("I fail too.")
              •
            AssertionError: I fail too.

            virtue.tests.samples.two_unsuccessful_tests.Bar.test_foo
            ========================================
            [FAIL]
            Traceback (most recent call last):•
              File "•unittest/case.py•", line •, in •
                •
              File "•virtue/tests/samples/two_unsuccessful_tests.py•", line 9, in test_bar
                self.fail("I fail.")
              •
            AssertionError: I fail.

            virtue.tests.samples.two_unsuccessful_tests.Foo.test_bar
            ----------------------------------------
            Ran 5 tests in 0.000s

            FAILED (successes=3, failures=2)
            """,  # noqa: E501
        )

    def test_single_test(self):
        self.assertOutputIs(
            tests=["virtue.tests.samples.one_successful_test"],
            expected="""
            virtue.tests.samples.one_successful_test
              Foo
                test_foo ...                    [OK]

            ----------------------------------------
            Ran 1 test in 0.000s

            PASSED (successes=1)
            """,
        )

    def test_empty_run(self):
        self.assertOutputIs(
            tests=[],
            expected="""

            ----------------------------------------
            Ran 0 tests in 0.000s

            PASSED
            """,
        )

    def test_expected_failure(self):
        self.assertOutputIs(
            tests=["virtue.tests.samples.one_expected_failure"],
            expected="""
            virtue.tests.samples.one_expected_failure
              Foo
                test_foo ...                 [XFAIL]

            ========================================
            [XFAIL]

            virtue.tests.samples.one_expected_failure.Foo.test_foo
            ----------------------------------------
            Ran 1 test in 0.000s

            PASSED (expected_failures=1)
            """,
        )

    def test_unexpected_success(self):
        self.assertOutputIs(
            tests=["virtue.tests.samples.failures_and_unexpected_passes"],
            expected="""
            virtue.tests.samples.failures_and_unexpected_passes
              Foo
                test_bar ...    [UNEXPECTED SUCCESS]
                test_baz ...    [UNEXPECTED SUCCESS]
                test_foo ...                  [FAIL]
                test_quux ...   [UNEXPECTED SUCCESS]
                test_spam ...                   [OK]

            ========================================
            [FAIL]
            Traceback (most recent call last):
              File "•unittest/case.py•", line •, in •
                •
              File "•/failures_and_unexpected_passes.py•", line •, in test_foo
                self.fail("Nope!")
              •
            AssertionError: Nope!

            virtue.tests.samples.failures_and_unexpected_passes.Foo.test_foo
            ========================================
            [UNEXPECTED SUCCESS]

            virtue.tests.samples.failures_and_unexpected_passes.Foo.test_bar
            virtue.tests.samples.failures_and_unexpected_passes.Foo.test_baz
            virtue.tests.samples.failures_and_unexpected_passes.Foo.test_quux
            ----------------------------------------
            Ran 5 tests in 0.000s

            FAILED (successes=1, failures=1, unexpected_successes=3)
            """,
        )

    def test_subtests(self):
        self.assertOutputIs(
            tests=["virtue.tests.samples.subtests"],
            expected="""
            virtue.tests.samples.subtests
              Baz
                test_passing_nested_subtest ... [OK]
                test_passing_subtest ...        [OK]
              Foo
                test_no_subtests ...            [OK]
                test_subtests_one_fail_one_error
                  i=1 ...                     [FAIL]
                  i=3 ...                    [ERROR]

            ========================================
            [FAIL]
            Traceback (most recent call last):
              File "•unittest/case.py•", line •, in •
                •
              File "•/subtests.py•", line •, in test_subtests_one_fail_one_error
                self.fail("Fail!")
              •
            AssertionError: Fail!

            virtue.tests.samples.subtests.Foo.test_subtests_one_fail_one_error (i=1)
            ========================================
            [ERROR]
            Traceback (most recent call last):
              File "•unittest/case.py•", line •, in •
                •
              File "•/subtests.py•", line •, in test_subtests_one_fail_one_error
                raise ZeroDivisionError()•
            ZeroDivisionError•

            virtue.tests.samples.subtests.Foo.test_subtests_one_fail_one_error (i=3)
            ----------------------------------------
            Ran 4 tests with 7 subtests in 0.000s

            FAILED (successes=3, subtest_failures=1, subtest_errors=1)
            """,  # noqa: E501
        )

    def test_output_is_compressed(self):
        """
        Albeit not sorted, so still not terribly reliably :/.
        """
        self.assertOutputIs(
            tests=["virtue.tests.samples.repeated_similar_output"],
            expected="""
            virtue.tests.samples.repeated_similar_output
              Foo
                test_a ...                 [SKIPPED]
                test_b ...                 [SKIPPED]
                test_c ...                 [SKIPPED]

            ========================================
            [SKIPPED]
            Skipped!
            virtue.tests.samples.repeated_similar_output.Foo.test_a
            ========================================
            [SKIPPED]
            Skipped 2!
            virtue.tests.samples.repeated_similar_output.Foo.test_b
            virtue.tests.samples.repeated_similar_output.Foo.test_c
            ----------------------------------------
            Ran 3 tests in 0.000s

            PASSED (skips=3)
            """,
        )
