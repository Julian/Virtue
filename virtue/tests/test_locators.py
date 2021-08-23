from operator import attrgetter
from unittest import TestCase
import shutil

from twisted.python.filepath import FilePath
from twisted.python.reflect import fullyQualifiedName

from virtue import locators
from virtue.loaders import AttributeLoader


class TestObjectLocator(TestCase):
    def test_it_finds_tests_in_an_object_specified_by_name(self):
        locator = locators.ObjectLocator()
        self.assertEqual(
            list(locator.locate_by_name(fullyQualifiedName(self.__class__))),
            list(locator.locate_in(self.__class__)),
        )

    def test_it_can_locate_methods_directly_by_name(self):
        locator = locators.ObjectLocator()
        this_name = "test_it_can_locate_methods_directly_by_name"
        this_fully_qualified_name = ".".join(
            [fullyQualifiedName(self.__class__), this_name],
        )
        self.assertEqual(
            list(locator.locate_by_name(this_fully_qualified_name)),
            [AttributeLoader(cls=self.__class__, attribute=this_name)],
        )

    def test_it_can_locate_aliased_methods_directly_by_name(self):
        locator = locators.ObjectLocator()
        this_name = "test_it_can_locate_aliased_methods_directly_by_name"
        aliased_fully_qualified_name = ".".join(
            [self.__class__.__module__, "aliased"],
        )
        self.assertEqual(
            list(locator.locate_by_name(aliased_fully_qualified_name)),
            [AttributeLoader(cls=self.__class__, attribute=this_name)],
        )

    def test_it_finds_methods_on_test_cases(self):
        locator = locators.ObjectLocator(
            is_test_method=locators.prefixed_by("TEST"),
        )

        class ASampleTestCase(TestCase):
            def not_a_test(self): pass

            def TEST1(self): pass

            def TEST_2(self): pass

        cases = locator.locate_in(ASampleTestCase)
        self.assertEqual(
            sorted(cases, key=attrgetter("attribute")), [
                AttributeLoader(cls=ASampleTestCase, attribute="TEST1"),
                AttributeLoader(cls=ASampleTestCase, attribute="TEST_2"),
            ],
        )

    def test_by_default_it_looks_for_methods_prefixed_by_test(self):
        locator = locators.ObjectLocator()

        class ASampleTestCase(TestCase):
            def not_a_test(self): pass

            def TEST1(self): pass

            def test_foo(self): pass

            def testBar(self): pass

        cases = locator.locate_in(ASampleTestCase)
        self.assertEqual(
            sorted(cases, key=attrgetter("attribute")), [
                AttributeLoader(cls=ASampleTestCase, attribute="testBar"),
                AttributeLoader(cls=ASampleTestCase, attribute="test_foo"),
            ],
        )

    def test_it_loads_methods_from_dynamically_created_test_case_classes(self):
        locator = locators.ObjectLocator()
        from virtue.tests.samples.dynamic_test import TestFoo
        name = "virtue.tests.samples.dynamic_test.TestFoo.test_F0"
        self.assertEqual(
            list(locator.locate_by_name(name)),
            [AttributeLoader(cls=TestFoo, attribute="test_F0")],
        )

    def test_it_finds_test_case_classes_on_modules(self):
        locator = locators.ObjectLocator(
            is_test_class=(lambda attr, value: attr != "Foo"),
        )
        from virtue.tests.samples import module_for_TestObjectLocator as module
        cases = locator.locate_in(module)
        self.assertEqual(
            sorted(cases, key=attrgetter("attribute")), [
                AttributeLoader(cls=module.Baz, attribute="test_bar"),
                AttributeLoader(cls=module.Baz, attribute="test_baz"),
                AttributeLoader(cls=module.Bar, attribute="test_foo"),
                AttributeLoader(cls=module.OldStyle, attribute="test_old"),
            ],
        )

    def test_by_default_it_looks_for_classes_inheriting_TestCase(self):
        locator = locators.ObjectLocator()
        from virtue.tests.samples import module_for_TestObjectLocator as module
        cases = locator.locate_in(module)
        self.assertEqual(
            sorted(cases, key=attrgetter("attribute")), [
                AttributeLoader(cls=module.Foo, attribute="test_foo"),
            ],
        )

    def test_it_finds_test_cases_recursively_in_packages(self):
        locator = locators.ObjectLocator(
            is_test_module=(lambda name: name != "foo"),
        )
        package = self.create_package_with_tests(locator)
        cases = locator.locate_in(package)
        self.assertEqual(
            sorted(case.module.name for case in cases), [
                "virtue.tests.temp",
                "virtue.tests.temp.bar",
                "virtue.tests.temp.sub",
                "virtue.tests.temp.sub.test_quux",
                "virtue.tests.temp.test_baz",
            ],
        )

    def test_by_default_it_finds_test_cases_in_modules_named_test_(self):
        locator = locators.ObjectLocator()
        package = self.create_package_with_tests(locator)
        cases = locator.locate_in(package)
        self.assertEqual(
            sorted(case.module.name for case in cases), [
                "virtue.tests.temp.sub.test_quux",
                "virtue.tests.temp.test_baz",
            ],
        )

    def test_it_knows_what_it_does_not_know(self):
        with self.assertRaises(ValueError):
            locators.ObjectLocator().locate_in(object())

    def create_package_with_tests(self, locator):
        package_path = FilePath(__file__).sibling(b"temp")
        package_path.makedirs()
        self.addCleanup(shutil.rmtree, package_path.path)

        package_path.child(b"__init__.py").setContent(b"")
        package_path.child(b"bar.py").setContent(b"")
        package_path.child(b"test_baz.py").setContent(b"")

        subpackage = package_path.child(b"sub")
        subpackage.makedirs()
        subpackage.child(b"__init__.py").setContent(b"")
        subpackage.child(b"test_quux.py").setContent(b"")

        from virtue.tests import temp as package
        return package


# Used to check that we locate or blow up properly on unbound methods
aliased_attr = "test_it_can_locate_aliased_methods_directly_by_name"
aliased = getattr(TestObjectLocator, aliased_attr)
