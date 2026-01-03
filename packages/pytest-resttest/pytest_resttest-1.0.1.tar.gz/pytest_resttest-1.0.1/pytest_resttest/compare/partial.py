import asyncio
from typing import Any, ClassVar, Self

from ruamel.yaml import Constructor, Node, Representer, SequenceNode


class Unsorted(list[Any]):
    """A list type that does not require it's items to be sorted to pass the test. All items present in this
    example list must be present in response, only the order of the items is not important."""

    yaml_tag: ClassVar[str] = "!unsorted"

    def __eq__(self, other: Any) -> bool:
        # pylint: disable=import-outside-toplevel, cyclic-import
        from pytest_resttest.compare.complex_compare import complex_compare

        errors = asyncio.run(complex_compare(self, other, False, {}, ""))
        return not errors

    def __repr__(self) -> str:
        return f"Unsorted({super().__repr__()})"

    @classmethod
    def to_yaml(cls, representer: Representer, node: Node) -> SequenceNode:
        """
        Converts the Unsorted list to a YAML node.
        """

        return representer.represent_sequence(cls.yaml_tag, node)

    @classmethod
    def from_yaml(cls, constructor: Constructor, node: Node) -> Self:
        """
        Constructs an Unsorted list from a YAML node.
        """

        return cls(constructor.construct_sequence(node))


class PartialList(Unsorted):
    """A partially defined list. This list must contain all items present in this example list, but may also contain
    additional items. The order of the items is not important."""

    yaml_tag: ClassVar[str] = "!partial"

    def __eq__(self, other: Any) -> bool:
        # pylint: disable=import-outside-toplevel, cyclic-import
        from pytest_resttest.compare.complex_compare import complex_compare

        errors = asyncio.run(complex_compare(self, other, False, {}, ""))
        return not errors

    def __repr__(self) -> str:
        return f"PartialList({list.__repr__(self)})"
