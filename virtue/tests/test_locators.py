from operator import attrgetter
from unittest import TestCase

from virtue import locators
from virtue.loaders import AttributeLoader


class TestObjectLocator(TestCase):
    def test_it_finds_methods_on_test_cases(self):
        locator = locators.ObjectLocator(
            is_test_method=locators.prefixed_by("TEST"),
        )

        class ASampleTestCase(TestCase):
            def not_a_test(self): pass
            def TEST1(self): pass
            def TEST_2(self): pass

        cases = locator.locate_in(ASampleTestCase)
        self.assertEqual(
            sorted(cases, key=attrgetter("attr")), [
                AttributeLoader(cls=ASampleTestCase, attr="TEST1"),
                AttributeLoader(cls=ASampleTestCase, attr="TEST_2"),
            ],
        )

    def test_by_default_it_looks_for_methods_prefixed_by_test(self):
        locator = locators.ObjectLocator()

        class ASampleTestCase(TestCase):
            def not_a_test(self): pass
            def TEST1(self): pass
            def test_foo(self): pass
            def testBar(self): pass

        cases = locator.locate_in(ASampleTestCase)
        self.assertEqual(
            sorted(cases, key=attrgetter("attr")), [
                AttributeLoader(cls=ASampleTestCase, attr="testBar"),
                AttributeLoader(cls=ASampleTestCase, attr="test_foo"),
            ],
        )
