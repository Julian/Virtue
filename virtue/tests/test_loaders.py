from unittest import TestCase

from twisted.python.modules import getModule as get_module

from virtue import loaders, locators


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
            cls=self.__class__, attribute="test_repr",
        )
        self.assertEqual(
            repr(loader),
            "AttributeLoader(cls=<class 'virtue.tests.test_loaders.TestAttributeLoader'>, attribute='test_repr')",  # noqa: E501
        )


class TestModuleLoader(TestCase):

    locator = locators.ObjectLocator()

    def test_it_loads_modules(self):
        module = get_module("virtue.tests.samples.module_for_TestLoaders")
        loader = loaders.ModuleLoader(locator=self.locator, module=module)

        cases = module.load()
        self.assertEqual(
            list(loader.load()), [
                cases.Baz("test_bar"),
                cases.Baz("test_baz"),
                cases.Foo("test_foo"),
            ],
        )

    def test_eq_neq(self):
        virtue, os = get_module("virtue"), get_module("os")
        loader = loaders.ModuleLoader(locator=self.locator, module=virtue)
        self.assertTrue(
            loader == loaders.ModuleLoader(locator=self.locator, module=virtue)
        )
        self.assertFalse(
            loader != loaders.ModuleLoader(locator=self.locator, module=virtue)
        )
        self.assertFalse(
            loader == loaders.ModuleLoader(locator=self.locator, module=os),
        )
        self.assertTrue(
            loader != loaders.ModuleLoader(locator=self.locator, module=os),
        )

    def test_repr(self):
        virtue = get_module("virtue")
        loader = loaders.ModuleLoader(locator=self.locator, module=virtue)
        self.assertEqual(
            repr(loader), "ModuleLoader(module=PythonModule<'virtue'>)",
        )
