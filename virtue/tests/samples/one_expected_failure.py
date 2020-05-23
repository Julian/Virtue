from unittest import TestCase, expectedFailure


class Foo(TestCase):
    @expectedFailure
    def test_foo(self):
        self.fail("I fail!")
