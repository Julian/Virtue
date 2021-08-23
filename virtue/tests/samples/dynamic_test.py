from unittest import TestCase


def create_test(name):
    methods = {f"test_{i}{j}": lambda _: None for j, i in enumerate(name)}
    return type(f"Test{name}", (TestCase,), methods)


TestFoo = create_test("Foo")
