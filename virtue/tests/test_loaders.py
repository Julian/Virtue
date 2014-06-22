from unittest import TestCase

from virtue import loaders


class TestAttributeLoader(TestCase):
    def test_eq_neq(self):
        cls = self.__class__
        loader = loaders.AttributeLoader(cls=cls, attr="test_eq")
        self.assertTrue(
            loader == loaders.AttributeLoader(cls=cls, attr="test_eq"),
        )
        self.assertFalse(
            loader != loaders.AttributeLoader(cls=cls, attr="test_eq"),
        )
        self.assertFalse(
            loader == loaders.AttributeLoader(cls=cls, attr="test_neq"),
        )
        self.assertTrue(
            loader != loaders.AttributeLoader(cls=cls, attr="test_neq"),
        )

    def test_repr(self):
        loader = loaders.AttributeLoader(cls=self.__class__, attr="test_repr")
        self.assertEqual(
            repr(loader),
            "<AttributeLoader cls='TestAttributeLoader' attr='test_repr'>",
        )
