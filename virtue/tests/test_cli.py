import os

from twisted.trial.reporter import TreeReporter

from virtue import cli
from virtue.compat import unittest


class TestParser(unittest.TestCase):
    def test_it_parses_out_tests(self):
        arguments = cli.parse_args(["foo", "bar", "baz"])
        self.assertEqual(arguments["tests"], ["foo", "bar", "baz"])

    def test_it_retrieves_built_in_reporters_by_name(self):
        arguments = cli.parse_args(["--reporter", "tree", "foo"])
        self.assertIsInstance(arguments["reporter"], TreeReporter)

    reporter = object()

    def test_it_retrieves_other_reporters_by_fully_qualified_name(self):
        arguments = cli.parse_args(
            ["--reporter", "virtue.tests.test_cli.TestParser.reporter", "abc"],
        )
        self.assertEqual(arguments["reporter"], self.reporter)


class TestMain(unittest.TestCase):
    # TODO: these write to stdout
    def test_it_exits_successfully_for_successful_runs(self):
        with self.assertRaises(SystemExit) as e:
            cli.main(
                [
                    "--reporter", "summary",
                    "virtue.tests.samples.one_successful_test",
                ],
            )
        self.assertEqual(e.exception.code, os.EX_OK)

    def test_it_exits_unsuccessfully_for_unsuccessful_runs(self):
        with self.assertRaises(SystemExit) as e:
            cli.main(
                [
                    "--reporter", "text",
                    "virtue.tests.samples.one_unsuccessful_test",
                ],
            )
        self.assertNotEqual(e.exception.code, os.EX_OK)

    def test_it_exits_unsuccessfully_for_unknown_reporters(self):
        with self.assertRaises(SystemExit) as e:
            cli.main(
                [
                    "--reporter", "non-existent reporter",
                    "virtue.tests.samples.one_unsuccessful_test",
                ],
            )
        self.assertNotEqual(e.exception.code, os.EX_OK)
