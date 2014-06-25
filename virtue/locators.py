from unittest import TestCase
from inspect import isclass, ismethod, ismodule

from twisted.python.modules import getModule as get_module
from twisted.python.reflect import namedAny as named_any

from virtue.loaders import AttributeLoader, ModuleLoader


def prefixed_by(prefix):
    """
    Make a callable returning True for names starting with the given prefix.

    The returned callable takes two arguments, the attribute or name of
    the object, and possibly its corresponding value (which is ignored),
    as suitable for use with :meth:`ObjectLocator.is_test_module` and
    :meth:`ObjectLocator.is_test_method`\ .

    """

    def prefixed_by_(name, value=None):
        return name.startswith(prefix)
    prefixed_by_.__name__ += prefix
    return prefixed_by_


def inherits_from_TestCase(attr, cls):
    return issubclass(cls, TestCase)


class ObjectLocator(object):
    """
    I locate test cases on an object: a package, module or test class.

    """

    def __init__(
        self,
        is_test_method=prefixed_by("test"),
        is_test_class=inherits_from_TestCase,
        is_test_module=prefixed_by("test_"),
    ):
        """
        Initialize the object locator.

        :argument callable is_test_method: decide whether the provided object
            is a test method or not. By default, callable objects whose names
            (``__name__``\ s) start with ``test_`` are considered test methods.
        :argument callable is_test_class: decide whether the provided object
            is a test class or not. By default, objects inheriting from
            :class:`unittest.TestCase` are considered test cases.
        :argument callable is_test_module: decide whether the provided object
            is a test module or not. By default, modules whose names start with
            ``test_`` are considered to be test modules.
        :returns: an iterable of test loaders for the located tests

        """

        self.is_test_method = is_test_method
        self.is_test_module = is_test_module
        self.is_test_class = is_test_class

    def locate_by_name(self, name):
        """
        Locate any tests found in the object referred to by the given name.

        The name should be a fully qualified object name. (E.g., the fully
        qualified object name of this function is
        ``virtue.locators.ObjectLocator.locate_by_name``\ ).

        """

        obj = named_any(name)
        if ismethod(obj):
            class_name, dot, method_name = name.rpartition(".")
            cls = named_any(class_name)

            is_aliased = not isclass(cls)
            if is_aliased:
                cls, method_name = obj.im_class, obj.__name__

            return [AttributeLoader(cls=cls, attr=method_name)]
        return self.locate_in(obj)

    def locate_in(self, obj):
        """
        Attempt to locate the test cases in the given object (of any kind).

        """

        # We don't use inspect.getmembers because its predicate only
        # takes the value, not the attr name.
        if ismodule(obj):
            is_package = getattr(obj, "__path__", None)
            if is_package is not None:
                return self.locate_in_package(obj)
            return self.locate_in_module(obj)
        elif isclass(obj):
            return self.locate_in_class(obj)
        else:
            raise ValueError(
                "Can't determine the appropriate way to load {0!r}".format(
                    obj,
                )
            )

    def locate_in_package(self, package):
        """
        Locate all of the test cases contained in the given package.

        """

        for module in get_module(package.__name__).walkModules():
            _, _, name = module.name.rpartition(".")
            if self.is_test_module(name):
                yield ModuleLoader(locator=self, module=module)

    def locate_in_module(self, module):
        """
        Locate all of the test cases contained in the given module.

        """

        for attr in dir(module):
            value = getattr(module, attr, None)
            if isclass(value) and self.is_test_class(attr, value):
                for test_case in self.locate_in_class(value):
                    yield test_case

    def locate_in_class(self, cls):
        """
        Locate the methods on the given class that are test cases.

        """

        for attr in dir(cls):
            value = getattr(cls, attr, None)
            if callable(value) and self.is_test_method(attr, value):
                yield AttributeLoader(cls=cls, attr=attr)
