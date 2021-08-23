from inspect import isclass, ismodule
from unittest import TestCase

from twisted.python.modules import getModule as get_module
from twisted.python.reflect import ModuleNotFound, ObjectNotFound
from twisted.python.reflect import fullyQualifiedName as fully_qualified_name
from twisted.python.reflect import namedAny as named_any
from twisted.trial.runner import filenameToModule as filename_to_module
import attr

from virtue.loaders import AttributeLoader, ModuleLoader


def prefixed_by(prefix):
    """
    Make a callable returning True for names starting with the given prefix.

    The returned callable takes two arguments, the attribute or name of
    the object, and possibly its corresponding value (which is ignored),
    as suitable for use with `ObjectLocator.is_test_module` and
    `ObjectLocator.is_test_method`.

    """

    def prefixed_by_(name, value=None):
        return name.startswith(prefix)
    prefixed_by_.__name__ += prefix
    return prefixed_by_


def inherits_from_TestCase(attr, cls):
    return issubclass(cls, TestCase)


@attr.s
class ObjectLocator(object):
    """
    I locate test cases on an object: a package, module or test class.

    Arguments:

        is_test_method (collections.abc.Callable):

            decide whether the provided object is a test method
            or not. By default, callable objects whose names
            (``__name__``s) start with ``test_`` are considered
            test methods.

        is_test_class (collections.abc.Callable):

            decide whether the provided object is a test
            class or not. By default, objects inheriting from
            `unittest.TestCase` are considered test cases.

        is_test_module (collections.abc.Callable):

            decide whether the provided object is a test module
            or not. By default, modules whose names start with
            ``test_`` are considered to be test modules.

    """

    #: Whether an object is a test method or not
    is_test_method = attr.ib(default=prefixed_by("test"), repr=False)
    #: Whether an object is a test class or not
    is_test_class = attr.ib(default=inherits_from_TestCase, repr=False)
    #: Whether an object is a test module or not
    is_test_module = attr.ib(default=prefixed_by("test_"), repr=False)

    def locate_by_name(self, name):
        """
        Locate any tests found in the object referred to by the given name.

        The name should be a fully qualified object name. (E.g., the fully
        qualified object name of this function is
        ``virtue.locators.ObjectLocator.locate_by_name``).

        A path may also alternatively used, but no `PYTHONPATH`
        modification will be done, so the file must be importable
        without modification.
        """

        try:
            obj = named_any(name)
        except (ModuleNotFound, ObjectNotFound):
            obj = filename_to_module(name)

        try:
            return self.locate_in(obj)
        except ValueError:
            fqon = fully_qualified_name(obj)
            class_name, _, method_name = fqon.rpartition(".")

            try:
                cls = named_any(class_name)
            except AttributeError:
                class_name, _, method_name = name.rpartition(".")
                cls = named_any(class_name)
                if isclass(cls):
                    return [AttributeLoader(cls=cls, attribute=method_name)]
            else:
                if isclass(cls):
                    return [AttributeLoader(cls=cls, attribute=method_name)]
            raise

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

        for attribute in dir(module):
            value = getattr(module, attribute, None)
            if isclass(value) and self.is_test_class(attribute, value):
                for test_case in self.locate_in_class(value):
                    yield test_case

    def locate_in_class(self, cls):
        """
        Locate the methods on the given class that are test cases.
        """

        for attribute in dir(cls):
            value = getattr(cls, attribute, None)
            if callable(value) and self.is_test_method(attribute, value):
                yield AttributeLoader(cls=cls, attribute=attribute)
