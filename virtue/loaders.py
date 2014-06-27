import itertools


class AttributeLoader(object):
    """
    I load a test case by instantiating a class with a given attribute name.

    This is the typical way that :class:`unittest.TestCase` methods are loaded:
    by calling ``TestCase("test_something")`` (and then by calling :meth:`run`
    on the resulting instance to run the selected test method).

    """

    def __init__(self, cls, attr):
        self.cls = cls
        self.attr = attr

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.cls == other.cls and self.attr == other.attr

    def __ne__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return not self == other

    def __repr__(self):
        return (
            "<{self.__class__.__name__} "
            "cls={self.cls.__name__!r} attr={self.attr!r}>".format(self=self)
        )

    def load(self):
        return [self.cls(self.attr)]


class ModuleLoader(object):
    """
    I load a test case by locating tests in the module with the given name.

    """

    def __init__(self, locator, module):
        self.locator = locator
        self.module = module

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.locator == other.locator and self.module == other.module

    def __ne__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return not self == other

    def __repr__(self):
        return (
            "<{self.__class__.__name__} module={self.module.name}>".format(
                self=self,
            )
        )

    def load(self):
        class_loaders = self.locator.locate_in_module(self.module.load())
        return itertools.chain.from_iterable(
            class_loader.load() for class_loader in class_loaders
        )
