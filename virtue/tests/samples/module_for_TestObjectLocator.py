from unittest import TestCase

something = 12


class Foo(TestCase):
    def stuff(self):
        pass

    def test_foo(self):
        pass


class Bar:
    def stuff(self):
        pass

    def test_foo(self):
        pass


class Baz:
    def test_bar(self):
        pass

    def test_baz(self):
        pass


def test_123():
    pass
