import abc
import unittest

from subclass_getter import get_subclasses
from subclass_getter import get_unique_subclasses


class TestGetSubclasses(unittest.TestCase):
    def test_get_subclasses_includes_indirect(self) -> None:
        class Base:
            pass

        class Child(Base):
            pass

        class GrandChild(Child):
            pass

        subclasses = list(get_subclasses(Base))
        self.assertIn(Child, subclasses)
        self.assertIn(GrandChild, subclasses)

    def test_get_subclasses_excludes_direct_abc_base(self) -> None:
        class Base:
            pass

        class AbstractChild(Base, abc.ABC):
            pass

        class ConcreteChild(AbstractChild):
            pass

        subclasses = list(get_subclasses(Base))
        self.assertNotIn(AbstractChild, subclasses)
        self.assertIn(ConcreteChild, subclasses)

    def test_get_subclasses_includes_abc_when_allowed(self) -> None:
        class Base:
            pass

        class AbstractChild(Base, abc.ABC):
            pass

        subclasses = list(get_subclasses(Base, exclude_abstract=False))
        self.assertIn(AbstractChild, subclasses)


class TestGetUniqueSubclasses(unittest.TestCase):
    def test_get_unique_subclasses_deduplicates_diamond(self) -> None:
        class Base:
            pass

        class Left(Base):
            pass

        class Right(Base):
            pass

        class Diamond(Left, Right):
            pass

        subclasses = list(get_subclasses(Base))
        unique_subclasses = list(get_unique_subclasses(Base))

        self.assertGreater(subclasses.count(Diamond), 1)
        self.assertEqual(unique_subclasses.count(Diamond), 1)
        self.assertEqual(
            set(unique_subclasses),
            {Left, Right, Diamond},
        )


if __name__ == "__main__":
    unittest.main()
