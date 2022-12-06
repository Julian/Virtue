from unittest import TestCase


class Foo(TestCase):
    def test_foo(self):
        pass

    def test_bar(self):
        for i in range(3):
            with self.subTest(i=i):
                pass


class Baz(TestCase):
    def test_quux(self):
        with self.subTest(quux="hello", spam="eggs"):
            with self.subTest(i=3):
                pass
