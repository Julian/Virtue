from unittest import TestCase


class Foo(TestCase):
    def test_no_subtests(self):
        pass

    def test_subtests_one_fail_one_error(self):
        for i in range(4):
            with self.subTest(i=i):
                if i == 1:
                    self.fail("Fail!")
                elif i == 3:
                    raise ZeroDivisionError()


class Baz(TestCase):
    def test_passing_nested_subtest(self):
        with self.subTest(quux="hello", spam="eggs"):
            with self.subTest(i=3):
                pass

    def test_passing_subtest(self):
        with self.subTest(eggs=3):
            pass
