from unittest import TestCase, expectedFailure


class Foo(TestCase):
    def test_foo(self):
        self.fail("Nope!")

    @expectedFailure
    def test_bar(self):
        pass

    @expectedFailure
    def test_baz(self):
        pass

    @expectedFailure
    def test_quux(self):
        pass

    def test_spam(self):
        pass
