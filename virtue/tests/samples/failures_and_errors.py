from unittest import TestCase


class Foo(TestCase):
    def test_foo(self):
        self.fail("Nope!")

    def test_bar(self):
        raise Exception("Boom!")

    def test_baz(self):
        raise Exception("Whiz!")

    def test_quux(self):
        raise Exception("Bang!")

    def test_spam(self):
        raise Exception("Hiss!")
