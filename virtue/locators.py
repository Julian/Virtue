"""
Loaders find tests which are referenced by names, preparing them for running.
"""

from pathlib import Path
from pkgutil import resolve_name, walk_packages
from unittest import TestCase
import importlib
import inspect
import itertools

from attrs import define, field

from virtue.loaders import AttributeLoader, ModuleLoader


class UnableToLoad(Exception):
    """
    A test couldn't be loaded.
    """


def _path_to_module(name: str):
    path = Path(name).resolve()
    if not path.exists():
        raise FileNotFoundError(name)

    if path.is_file():
        parts = [path.stem] if path.stem != "__init__" else []
        current = path.parent
    else:
        parts = []
        current = path

    while (current / "__init__.py").exists():
        parts.append(current.name)
        current = current.parent

    return importlib.import_module(".".join(reversed(parts)))


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
    """
    Return true if a class inherits from `unittest.TestCase`.
    """
    return issubclass(cls, TestCase)


@define
class ObjectLocator:
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
    is_test_method = field(default=prefixed_by("test"), repr=False)
    #: Whether an object is a test class or not
    is_test_class = field(default=inherits_from_TestCase, repr=False)
    #: Whether an object is a test module or not
    is_test_module = field(default=prefixed_by("test_"), repr=False)

    def __attrs_post_init__(self):
        is_cls, self.is_test_class = (
            self.is_test_class,
            lambda attr, cls: inspect.isclass(cls) and is_cls(attr, cls),
        )
        is_meth, self.is_test_method = (
            self.is_test_method,
            lambda attr, val: callable(val) and is_meth(attr, val),
        )

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
            obj = resolve_name(name)
        except ValueError:
            obj = _path_to_module(name)

        try:
            return self.locate_in(obj)
        except UnableToLoad:
            class_name, _, method_name = name.rpartition(".")

            try:
                cls = resolve_name(class_name)
            except ValueError:
                class_name, _, method_name = name.rpartition(".")
                cls = resolve_name(class_name)
                if inspect.isclass(cls):
                    return [AttributeLoader(cls=cls, attribute=method_name)]
            else:
                if inspect.isclass(cls):
                    return [AttributeLoader(cls=cls, attribute=method_name)]

            # Aliased attributes
            fqon = f"{obj.__module__}.{obj.__qualname__}"
            class_name, _, method_name = fqon.rpartition(".")
            cls = resolve_name(class_name)
            if inspect.isclass(cls):
                return [AttributeLoader(cls=cls, attribute=method_name)]

            raise

    def locate_in(self, obj):
        """
        Attempt to locate the test cases in the given object (of any kind).
        """
        # We don't use inspect.getmembers because its predicate only
        # takes the value, not the attr name.
        if inspect.ismodule(obj):
            is_package = getattr(obj, "__path__", None)
            if is_package is not None:
                return self.locate_in_package(obj)
            return self.locate_in_module(obj)
        elif inspect.isclass(obj):
            return self.locate_in_class(obj)
        else:
            raise UnableToLoad(
                f"Can't determine the appropriate way to load {obj!r}",
            )

    def locate_in_package(self, package):
        """
        Locate all of the test cases contained in the given package.
        """
        submodules = walk_packages(
            path=package.__path__,
            prefix=f"{package.__name__}.",
        )
        names = itertools.chain(
            [package.__name__],
            (info.name for info in submodules),
        )
        for fqmn in names:
            _, _, name = fqmn.rpartition(".")
            if self.is_test_module(name):
                yield ModuleLoader(locator=self, name=fqmn)

    def locate_in_module(self, module):
        """
        Locate all of the test cases contained in the given module.
        """
        for attribute, value in inspect.getmembers(module):
            if self.is_test_class(attribute, value):
                yield from self.locate_in_class(value)

    def locate_in_class(self, cls):
        """
        Locate the methods on the given class that are test cases.
        """
        for attribute, value in inspect.getmembers(cls):
            if self.is_test_method(attribute, value):
                yield AttributeLoader(cls=cls, attribute=attribute)
