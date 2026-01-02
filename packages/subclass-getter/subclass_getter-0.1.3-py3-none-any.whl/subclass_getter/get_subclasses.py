"""Utilities for recursively retrieving subclasses of a given class."""

from abc import ABC
from collections.abc import Generator
from typing import TypeVar

ClassType = TypeVar("ClassType")


def get_subclasses(
    base_class: type[ClassType], exclude_abstract: bool = True
) -> Generator[type[ClassType], None, None]:
    """
    Recursively yield all subclasses of a given base class using breadth-first traversal.

    This function performs a breadth-first traversal of the class hierarchy,
    yielding each subclass as it's discovered. Note that the same subclass
    may be yielded multiple times if it appears in multiple inheritance paths.

    Args:
        base_class: The base class whose subclasses to retrieve.
        exclude_abstract: Wherethere to exclude abstract subclasses from generator result.

    Yields:
        Each subclass found in the hierarchy, including indirect subclasses.
        Subclasses may be yielded multiple times if they have multiple parent
        classes that are themselves subclasses of base_class.

    Example:
        >>> class Animal: pass
        >>> class Mammal(Animal): pass
        >>> class Dog(Mammal): pass
        >>> list(get_subclasses(Animal))
        [<class 'Mammal'>, <class 'Dog'>]
    """
    to_process = [base_class]
    while to_process:
        current = to_process.pop()
        for subclass in current.__subclasses__():
            if not exclude_abstract or ABC not in subclass.__bases__:
                yield subclass
            to_process.append(subclass)


def get_unique_subclasses(
    base_class: type[ClassType],
    exclude_abstract: bool = True,
) -> Generator[type[ClassType], None, None]:
    """
    Recursively yield unique subclasses of a given base class using breadth-first traversal.

    This function yields each subclass exactly once, regardless of how many
    inheritance paths lead to it. Memory-efficient as it uses a generator and
    only tracks seen classes, not all results.

    Particularly useful with diamond inheritance where a class may appear
    multiple times in get_subclasses() output.

    Args:
        base_class: The base class whose subclasses to retrieve.
        exclude_abstract: Wherethere to exclude abstract subclasses from generator result.

    Yields:
        Each unique subclass found in the hierarchy, including indirect subclasses.

    Example:
        >>> class Base: pass
        >>> class Left(Base): pass
        >>> class Right(Base): pass
        >>> class Diamond(Left, Right): pass
        >>> # get_subclasses yields Diamond twice (via Left and Right)
        >>> len(list(get_subclasses(Base)))
        4
        >>> # get_unique_subclasses yields each class only once
        >>> len(list(get_unique_subclasses(Base)))
        3
    """
    seen = set()
    for subclass in get_subclasses(base_class):
        if subclass not in seen:
            seen.add(subclass)
            if not exclude_abstract or ABC not in subclass.__bases__:
                yield subclass
