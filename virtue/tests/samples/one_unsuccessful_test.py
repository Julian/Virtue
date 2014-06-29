from unittest import TestCase


class Foo(TestCase):
    def test_foo(self):
        self.fail("I fail!")
