import itertools

import attr


@attr.s
class GroupLoader:

    _cases = attr.ib()
    _args = attr.ib(default=())
    _kwargs = attr.ib(default={})

    def load(self):
        return self._cases(*self._args, **self._kwargs)


@attr.s
class ModuleLoader:
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
