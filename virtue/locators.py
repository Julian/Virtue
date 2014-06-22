from unittest import TestCase
import inspect

from virtue.loaders import AttributeLoader


def prefixed_by(prefix):
    """
    Make a callable returning True for names starting with the given prefix.

    The returned callable takes two arguments, the attribute
    name and its corresponding value, as suitable for use with
    :meth:`ObjectLocator.is_test_method`\ , but in this case the value
    is ignored.

    """

    def prefixed_by_(attr, value):
        return attr.startswith(prefix)
    prefixed_by_.__name__ += prefix
    return prefixed_by_


def inherits_from_TestCase(attr, cls):
    return issubclass(cls, TestCase)


class ObjectLocator(object):
    """
    I locate test cases on an object: a package, module, test class, or method.

    """

    def __init__(
        self,
        is_test_method=prefixed_by("test"),
        is_test_class=inherits_from_TestCase,
    ):
        """
        Initialize the object locator.

        :argument callable is_test_method: decide whether the provided object
            is a test method or not. By default, callable objects whose names
            (``__name__``\ s) start with ``test_`` are considered test methods.
        :argument callable is_test_class: decide whether the provided object
            is a test class or not. By default, objects inheriting from
            :class:`unittest.TestCase` are considered test cases.
        :returns: an iterable of test loaders for the located tests

        """

        self.is_test_method = is_test_method
        self.is_test_class = is_test_class

    def locate_in(self, obj):
        """
        Attempt to locate the test cases in the given object (of any kind).

        """

        # We don't use inspect.getmembers because its predicate only
        # takes the value, not the attr name.
        if inspect.ismodule(obj):
            return self.locate_in_module(obj)
        else:
            return self.locate_in_class(obj)

    def locate_in_module(self, module):
        """
        Locate all of the test cases contained in the given module.

        """

        for attr in dir(module):
            value = getattr(module, attr, None)
            if inspect.isclass(value) and self.is_test_class(attr, value):
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
