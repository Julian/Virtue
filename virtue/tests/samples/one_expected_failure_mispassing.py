from unittest import TestCase, expectedFailure


class Foo(TestCase):
    @expectedFailure
    def test_foo(self):
        pass  # Look ma! I don't fail!
