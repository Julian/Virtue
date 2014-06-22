from virtue.loaders import AttributeLoader


def prefixed_by(prefix):
    """
    Make a callable returning True for names starting with the given prefix.

    The returned callable takes two arguments, the attribute name and its
    corresponding value, as suitable for use with
    :meth:`ObjectLocator.is_test_method`\ , but in this case the value is
    ignored.

    """

    def prefixed_by_(attr, value):
        return attr.startswith(prefix)
    prefixed_by_.__name__ += prefix
    return prefixed_by_


class ObjectLocator(object):
    """
    I locate test cases on an object: a package, module, test class, or method.

    """

    def __init__(self, is_test_method=prefixed_by("test")):
        """
        Initialize the object locator.

        :argument callable is_test_method: decide whether the provided object
            is a test method or not. By default, callable objects whose names
            (``__name__``\ s) start with ``test_`` are considered test methods.

        """

        self.is_test_method = is_test_method

    def locate_in(self, obj):
        """
        Locate the test cases in the given object.

        """

        # We don't use inspect.getmembers because its predicate only
        # takes the value, not the attr name.
        for attr in dir(obj):
            value = getattr(obj, attr, None)
            if callable(value) and self.is_test_method(attr, value):
                yield AttributeLoader(cls=obj, attr=attr)
