from twisted.python.modules import getModule as get_module

from virtue import loaders, locators
from virtue.compat import unittest


class TestAttributeLoader(unittest.TestCase):
    def test_eq_neq(self):
        cls = self.__class__
        loader = loaders.AttributeLoader(cls=cls, attr="test_eq")
        self.assertTrue(
            loader == loaders.AttributeLoader(cls=cls, attr="test_eq"),
        )
        self.assertFalse(
            loader != loaders.AttributeLoader(cls=cls, attr="test_eq"),
        )
        self.assertFalse(
            loader == loaders.AttributeLoader(cls=cls, attr="test_neq"),
        )
        self.assertTrue(
            loader != loaders.AttributeLoader(cls=cls, attr="test_neq"),
        )

    def test_repr(self):
        loader = loaders.AttributeLoader(cls=self.__class__, attr="test_repr")
        self.assertEqual(
            repr(loader),
            "<AttributeLoader cls='TestAttributeLoader' attr='test_repr'>",
        )


class TestModuleLoader(unittest.TestCase):
    def test_eq_neq(self):
        virtue, itertools = get_module("virtue"), get_module("itertools")
        locator = locators.ObjectLocator()
        loader = loaders.ModuleLoader(locator=locator, module=virtue)
        self.assertTrue(
            loader == loaders.ModuleLoader(locator=locator, module=virtue),
        )
        self.assertFalse(
            loader != loaders.ModuleLoader(locator=locator, module=virtue),
        )
        self.assertFalse(
            loader == loaders.ModuleLoader(locator=locator, module=itertools),
        )
        self.assertTrue(
            loader != loaders.ModuleLoader(locator=locator, module=itertools),
        )

    def test_repr(self):
        virtue = get_module("virtue")
        locator = locators.ObjectLocator()
        loader = loaders.ModuleLoader(locator=locator, module=virtue)
        self.assertEqual(repr(loader), "<ModuleLoader module=virtue>")
