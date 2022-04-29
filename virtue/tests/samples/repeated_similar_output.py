from unittest import TestCase


class Foo(TestCase):
    def test_a(self):
        self.skipTest("Skipped!")

    def test_b(self):
        self.skipTest("Skipped 2!")

    def test_c(self):
        self.skipTest("Skipped 2!")
