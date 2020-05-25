from unittest import TestCase
import os

from twisted.trial.reporter import TreeReporter

from virtue import _cli


def DumbReporter():
    return 12


class TestParser(TestCase):
    def parse_args(self, argv):
        return _cli.main.make_context("virtue", argv).params

    def test_it_parses_out_tests(self):
        arguments = self.parse_args(["foo", "bar", "baz"])
        self.assertEqual(list(arguments["tests"]), ["foo", "bar", "baz"])

    def test_it_retrieves_built_in_reporters_by_name(self):
        arguments = self.parse_args(["--reporter", "tree", "foo"])
        self.assertIsInstance(arguments["reporter"], TreeReporter)

    def test_it_retrieves_other_reporters_by_fully_qualified_name(self):
        arguments = self.parse_args(
            ["--reporter", "virtue.tests.test_cli.DumbReporter", "abc"],
        )
        self.assertEqual(arguments["reporter"], DumbReporter())

    def test_stop_after(self):
        arguments = self.parse_args(["-xxx", "bar", "baz"])
        self.assertEqual(
            (arguments["stop_after"], list(arguments["tests"])),
            (3, ["bar", "baz"]),
        )

    def test_stop_after_default(self):
        arguments = self.parse_args(["-x", "bar", "baz"])
        self.assertEqual(
            (arguments["stop_after"], list(arguments["tests"])),
            (1, ["bar", "baz"]),
        )


class TestMain(TestCase):
    # TODO: these write to stdout
    def test_it_exits_successfully_for_successful_runs(self):
        with self.assertRaises(SystemExit) as e:
            _cli.main(
                [
                    "--reporter", "summary",
                    "virtue.tests.samples.one_successful_test",
                ],
            )
        self.assertEqual(e.exception.code, os.EX_OK)

    def test_it_exits_unsuccessfully_for_unsuccessful_runs(self):
        with self.assertRaises(SystemExit) as e:
            _cli.main(
                [
                    "--reporter", "text",
                    "virtue.tests.samples.one_unsuccessful_test",
                ],
            )
        self.assertNotEqual(e.exception.code, os.EX_OK)

    def test_it_exits_unsuccessfully_for_unknown_reporters(self):
        with self.assertRaises(SystemExit) as e:
            _cli.main(
                [
                    "--reporter", "non-existent reporter",
                    "virtue.tests.samples.one_unsuccessful_test",
                ],
            )
        self.assertNotEqual(e.exception.code, os.EX_OK)
