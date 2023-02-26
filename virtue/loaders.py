"""
Loaders take a named test case and load the test appropriately.
"""
from __future__ import annotations

from typing import TYPE_CHECKING
import itertools

from attrs import field, frozen

if TYPE_CHECKING:
    import twisted.python.modules

    from virtue.locators import ObjectLocator


@frozen
class AttributeLoader:
    """
    I load a test case by instantiating a class with a given attribute name.

    This is the typical way that `unittest.TestCase` methods are loaded:
    by calling ``TestCase("test_something")`` (and then by calling
    :meth:`~unittest.TestCase.run` on the resulting instance to run the
    selected test method).
    """

    cls: type
    attribute: str

    def load(self):
        """
        Load as a single test.
        """
        return [self.cls(self.attribute)]


@frozen
class ModuleLoader:
    """
    I load a test case by locating tests in the module with the given name.
    """

    locator: ObjectLocator = field(repr=False)
    module: twisted.python.modules.PythonModule

    def load(self):
        """
        Load all test cases in the module.
        """
        class_loaders = self.locator.locate_in_module(self.module.load())
        return itertools.chain.from_iterable(
            class_loader.load() for class_loader in class_loaders
        )
