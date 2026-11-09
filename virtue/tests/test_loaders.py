from unittest import TestCase

from virtue import loaders, locators
from virtue.tests.samples import module_for_TestLoaders


class TestAttributeLoader(TestCase):
    def test_it_loads_attributes(self):
        cls, attr = self.__class__, "test_it_loads_attributes"
        loader = loaders.AttributeLoader(cls=cls, attribute=attr)
        self.assertEqual(list(loader.load()), [cls(attr)])

    def test_eq_neq(self):
        cls = self.__class__
        loader = loaders.AttributeLoader(cls=cls, attribute="test_eq")
        self.assertTrue(
            loader == loaders.AttributeLoader(cls=cls, attribute="test_eq"),
        )
        self.assertFalse(
            loader != loaders.AttributeLoader(cls=cls, attribute="test_eq"),
        )
        self.assertFalse(
            loader == loaders.AttributeLoader(cls=cls, attribute="test_neq"),
        )
        self.assertTrue(
            loader != loaders.AttributeLoader(cls=cls, attribute="test_neq"),
        )

    def test_repr(self):
        loader = loaders.AttributeLoader(
            cls=self.__class__,
            attribute="test_repr",
        )
        self.assertEqual(
            repr(loader),
            "AttributeLoader(cls=<class 'virtue.tests.test_loaders.TestAttributeLoader'>, attribute='test_repr')",  # noqa: E501
        )


class TestModuleLoader(TestCase):
    locator = locators.ObjectLocator()

    def test_it_loads_modules(self):
        loader = loaders.ModuleLoader(
            locator=self.locator,
            name="virtue.tests.samples.module_for_TestLoaders",
        )

        self.assertEqual(
            list(loader.load()),
            [
                module_for_TestLoaders.Baz("test_bar"),
                module_for_TestLoaders.Baz("test_baz"),
                module_for_TestLoaders.Foo("test_foo"),
            ],
        )

    def test_eq_neq(self):
        loader = loaders.ModuleLoader(locator=self.locator, name="virtue")
        self.assertEqual(
            loader,
            loaders.ModuleLoader(locator=self.locator, name="virtue"),
        )
        self.assertNotEqual(
            loader,
            loaders.ModuleLoader(locator=self.locator, name="os"),
        )

    def test_repr(self):
        loader = loaders.ModuleLoader(locator=self.locator, name="virtue")
        self.assertEqual(
            repr(loader),
            "ModuleLoader(name='virtue')",
        )
