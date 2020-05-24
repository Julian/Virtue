from unittest import TestCase
import warnings


class Foo(TestCase):
    def test_foo(self):
        pass

    def test_bar(self):
        warnings.warn("Oh no! A Warning!")
