import itertools

import attr


@attr.s
class AttributeLoader(object):
    """
    I load a test case by instantiating a class with a given attribute name.

    This is the typical way that `unittest.TestCase` methods are loaded:
    by calling ``TestCase("test_something")`` (and then by calling
    :meth:`~unittest.TestCase.run` on the resulting instance to run the
    selected test method).
    """

    cls = attr.ib()
    attribute = attr.ib()

    def load(self):
        return [self.cls(self.attribute)]


@attr.s
class ModuleLoader(object):
    """
    I load a test case by locating tests in the module with the given name.
    """

    locator = attr.ib(repr=False)
    module = attr.ib()

    def load(self):
        class_loaders = self.locator.locate_in_module(self.module.load())
        return itertools.chain.from_iterable(
            class_loader.load() for class_loader in class_loaders
        )
