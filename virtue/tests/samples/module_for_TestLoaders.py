from unittest import TestCase


class Foo(TestCase):
    def stuff(self):
        pass

    def test_foo(self):
        pass


class Baz(TestCase):
    def test_bar(self):
        pass

    def test_baz(self):
        pass
