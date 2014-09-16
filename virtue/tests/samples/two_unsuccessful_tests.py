from unittest import TestCase


class Foo(TestCase):
    def test_foo(self):
        pass

    def test_bar(self):
        self.fail("I fail.")


class Bar(TestCase):
    def test_foo(self):
        self.fail("I fail too.")

    def test_bar(self):
        pass
