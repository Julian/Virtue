from unittest import TestCase

something = 12


class Foo(TestCase):
    def stuff(self):
        pass

    def test_foo(self):
        pass


class Bar(object):
    def stuff(self):
        pass

    def test_foo(self):
        pass


class Baz(object):
    def test_bar(self):
        pass

    def test_baz(self):
        pass


class OldStyle:
    def thing(self):
        pass

    def test_old(self):
        pass


def test_123():
    pass
