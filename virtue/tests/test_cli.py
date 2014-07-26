from virtue import cli
from virtue.compat import unittest


class TestParser(unittest.TestCase):
    def test_it_parses_out_tests(self):
        arguments = cli.parse_args(["foo", "bar", "baz"])
        self.assertEqual(arguments["tests"], ["foo", "bar", "baz"])


class TestMain(unittest.TestCase):
    def test_it_exits_successfully_for_successful_runs(self):
        with self.assertRaises(SystemExit) as e:
            cli.main(["virtue.tests.samples.one_successful_test"])
        self.assertEqual(e.exception.code, 0)

    def test_it_exits_unsuccessfully_for_unsuccessful_runs(self):
        with self.assertRaises(SystemExit) as e:
            cli.main(["virtue.tests.samples.one_unsuccessful_test"])
        self.assertEqual(e.exception.code, 1)
