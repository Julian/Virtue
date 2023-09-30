from unittest import TestCase

from twisted.python.modules import getModule as get_module

from virtue import loaders, locators


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
        self.assertEqual(
            loader, loaders.ModuleLoader(locator=self.locator, module=virtue),
        )
        self.assertNotEqual(
            loader, loaders.ModuleLoader(locator=self.locator, module=os),
        )

    def test_repr(self):
        virtue = get_module("virtue")
        loader = loaders.ModuleLoader(locator=self.locator, module=virtue)
        self.assertEqual(
            repr(loader), "ModuleLoader(module=PythonModule<'virtue'>)",
        )
