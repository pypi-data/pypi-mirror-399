from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime
from typing import Any

from assertpy import assert_that
from pydantic import BaseModel, Field

from pytest_resttest.compare.partial import PartialList, Unsorted
from pytest_resttest.compare.repr import actual_error, actual_excessive, expected_error, format_msg, stringify_value
from pytest_resttest.jinja.evaluate import evaluate_jinja, is_template_string


def prefix_from_path(path: str) -> str:
    """Generate a prefix for error messages based on the path."""

    return f"{path}: " if path else ""


def is_simple_value(value: Any) -> bool:
    """
    Decides whether value is a simple or complex type. Simple types are unstructured scalars, like str, int, float, bool or None.
    """

    return isinstance(value, (str, bytes, int, float, bool, type(None)))


class CompareLine(BaseModel):
    """
    One line of comparison result.
    """

    value: Any
    description: str | None = None


class CompareResult(BaseModel):
    """
    Base class for comparison result.
    """

    error: bool = False

    @property
    def total_errors(self) -> int:
        """
        Returns number of total errors in the result structure.
        """

        if self.error:
            return 1

        return 0

    def __bool__(self) -> bool:
        return self.total_errors > 0

    def get_longest_line_length(self) -> int:
        """
        Returns longest line of the result length.
        """

        # pylint: disable=no-self-use

        return 0

    def format(self, indent: int = 0) -> str:
        """
        Format the comparison result as a string.
        """

        # pylint: disable=unused-argument

        return str(self)


class CompareResultSimple(CompareResult):
    """
    Simple comparison result, for simple values.
    """

    expected: CompareLine | None = None
    actual: CompareLine | None = None

    @property
    def expected_repr(self) -> str:
        """
        Format expected value as string.
        """

        if self.expected is None:
            return "None"

        return stringify_value(self.expected.value)

    @property
    def actual_repr(self) -> str:
        """
        Format actual value as string.
        """

        if self.actual is None:
            return "None"

        return stringify_value(self.actual.value)

    def format(self, indent: int = 0) -> str:
        out: list[str] = []

        if not self.error:
            if self.expected is not None:
                out.append(format_msg(self.expected_repr, self.expected.description, indent=indent))

            elif self.actual is not None:
                out.append(actual_excessive(self.actual_repr, self.actual.description, indent=indent))
        else:
            if self.expected is not None:
                out.append(expected_error(self.expected_repr, self.expected.description, indent=indent))

            if self.actual is not None:
                out.append(actual_error(self.actual_repr, self.actual.description, indent=indent))

        return "\n".join(out)

    def __str__(self) -> str:
        return self.format(self.get_longest_line_length())

    def get_longest_line_length(self) -> int:
        lengths: list[int] = []

        if self.expected is not None:
            head, *_ = self.expected_repr.splitlines()
            lengths.append(len(head))

        if self.actual is not None:
            head, *_ = self.actual_repr.splitlines()
            lengths.append(len(head))

        return max(lengths) if lengths else 0


class CompareResultComplex[ItemTypeT: CompareResult](CompareResult):
    """
    Result of comparison of complex types.
    """

    items: list[ItemTypeT] = Field(default_factory=list)

    @property
    def total_errors(self) -> int:
        return sum(item.total_errors for item in self.items) + (1 if self.error else 0)

    def format(self, indent: int = 0) -> str:
        out: list[str] = []

        for item in self.items:
            out.append(item.format(indent=indent))

        return "\n".join(out)

    def get_longest_line_length(self) -> int:
        lengths = [super().get_longest_line_length(), *[item.get_longest_line_length() for item in self.items]]

        return max(lengths) if lengths else 0

    def __str__(self) -> str:
        return self.format(self.get_longest_line_length())


class CompareListItem(CompareResult):
    """
    Mixin class for comparison result of item in list.
    """

    index: int


class CompareListItemSimple(CompareListItem, CompareResultSimple):
    """
    Comparison result of a simple item in a list.
    """

    @staticmethod
    def _prefix(text: str) -> str:
        head, *tail = text.splitlines()
        out = [f"- {head}"]

        if tail:
            out.extend([f"  {line}" for line in tail])

        return "\n".join(out)

    @property
    def expected_repr(self) -> str:
        return self._prefix(super().expected_repr)

    @property
    def actual_repr(self) -> str:
        return self._prefix(super().actual_repr)

    def format(self, indent: int = 0) -> str:
        return super().format(indent=indent + 2)  # account for "- " prefix


class CompareListItemComplex[ItemTypeT: CompareResult](CompareListItem, CompareResultComplex[ItemTypeT]):
    """
    Comparison result of a complex item in a list.
    """

    def format(self, indent: int = 0) -> str:
        out: list[str] = []
        head, *tail = str(super().format(indent)).splitlines()
        out.append(f"- {head}")
        out.extend([f"  {line}" for line in tail])
        return "\n".join(out)


class CompareDictKey(CompareResult):
    """
    Mixin class for comparison result of a key in a dictionary.
    """

    key: str


class CompareDictKeySimple(CompareDictKey, CompareResultSimple):
    """
    Comparison result of a simple key in a dictionary.
    """

    def _prefix_with_key(self, text: str) -> str:
        head, *tail = text.splitlines()
        out = [f"{self.key}: {head}"]

        if tail:
            out.extend([f"{' ' * (len(self.key) + 2)}{line}" for line in tail])

        return "\n".join(out)

    def _format_complex(self, value: str) -> str:
        out: list[str] = []
        dbg = str(value).splitlines()
        out.append(f"{self.key}:")
        out.extend([f"  {line}" for line in dbg])
        return "\n".join(out)

    @property
    def expected_repr(self) -> str:
        if self.expected and is_simple_value(self.expected.value):
            return self._prefix_with_key(super().expected_repr)

        return self._format_complex(super().expected_repr)

    @property
    def actual_repr(self) -> str:
        if self.actual and is_simple_value(self.actual.value):
            return self._prefix_with_key(super().actual_repr)

        return self._format_complex(super().actual_repr)


class CompareDictKeyComplex[ItemTypeT: CompareResult](CompareDictKey, CompareResultComplex[ItemTypeT]):
    """
    Comparison result of a complex key in a dictionary.
    """

    def format(self, indent: int = 0) -> str:
        out: list[str] = []
        dbg = str(super().format(indent)).splitlines()
        out.append(f"{self.key}:")
        out.extend([f"  {line}" for line in dbg])
        return "\n".join(out)


class MissingType:
    """
    Type representing missing value in comparison.
    """

    def __bool__(self) -> bool:
        return False


Missing = MissingType()


async def compare_dicts_v2(
    expected: dict[str, Any], actual: Any, partial_content: bool, context: dict[str, Any]
) -> CompareResult:
    """
    Compare two dictionaries, recursively.
    """

    if not isinstance(actual, dict):
        return CompareResultSimple(
            expected=CompareLine(value=expected, description=f"expected type: {type(expected).__name__}"),
            actual=CompareLine(value=actual, description=f"got type {type(actual).__name__}"),
            error=True,
        )

    all_keys = set(expected.keys()) | set(actual.keys())
    result = CompareResultComplex[CompareDictKey]()

    for key in sorted(all_keys):
        if key not in expected:
            if not partial_content:
                result.items.append(
                    CompareDictKeySimple(
                        key=key,
                        error=True,
                        actual=CompareLine(
                            value=actual[key], description="key not in expected response and partial match is disabled"
                        ),
                    )
                )
            else:
                result.items.append(
                    CompareDictKeySimple(
                        key=key, actual=CompareLine(value=actual[key], description="excessive content in actual response")
                    )
                )

        elif key not in actual:
            result.items.append(
                CompareDictKeySimple(
                    key=key, error=True, expected=CompareLine(value=expected[key], description="not found in actual response")
                )
            )

        else:
            compare_response = await complex_compare_v2(
                expected[key],
                actual[key],
                partial_content,
                context,
            )

            if isinstance(compare_response, CompareResultSimple):
                result.items.append(
                    CompareDictKeySimple(
                        key=key,
                        error=compare_response.error,
                        expected=compare_response.expected,
                        actual=compare_response.actual,
                    )
                )
            elif isinstance(compare_response, CompareResultComplex):
                result.items.append(
                    CompareDictKeyComplex(
                        key=key,
                        error=compare_response.error,
                        items=compare_response.items,
                    )
                )

    return result


async def compare_unsorted_lists_v2(
    expected: Unsorted, actual: Sequence[Any], partial_content: bool, context: dict[str, Any]
) -> CompareResult:
    """
    Compare two lists, without considering the order of items. Tries to find minimal differences.
    """

    actual = list(actual)
    result = CompareResultComplex[CompareListItem]()

    for i, value in enumerate(expected):
        min_errors = None
        min_response = None
        min_idx = None

        if not actual:
            # If actual is empty, we cannot find a match.
            result.items.append(
                CompareListItemSimple(
                    index=i, error=True, expected=CompareLine(value=value, description="missing item in actual list")
                )
            )
            continue

        for j, actual_value in enumerate(actual):
            compare_response = await complex_compare_v2(value, actual_value, partial_content, context)
            errors = compare_response.total_errors

            if min_errors is None or errors < min_errors:
                min_errors = errors
                min_response = compare_response
                min_idx = j

            if not errors:
                break

        actual.pop(min_idx)

        if isinstance(min_response, CompareResultSimple):
            result.items.append(
                CompareListItemSimple(
                    index=i,
                    error=min_response.error,
                    expected=min_response.expected,
                    actual=min_response.actual,
                )
            )
        elif isinstance(min_response, CompareResultComplex):
            result.items.append(
                CompareListItemComplex(
                    index=i,
                    error=min_response.error,
                    items=min_response.items,
                )
            )

    if not isinstance(expected, PartialList):
        if actual:
            for item in actual:
                result.items.append(
                    CompareListItemSimple(
                        index=-1, error=True, actual=CompareLine(value=item, description="excessive item in actual list")
                    )
                )

    return result


async def compare_lists_v2(expected: Sequence[Any], actual: Any, partial_content: bool, context: dict[str, Any]) -> CompareResult:
    """
    Compare two lists, recursively.
    """

    if not isinstance(actual, Sequence) or isinstance(actual, (str, bytes)):
        return CompareResultSimple(
            expected=CompareLine(value=expected, description="expected type list"),
            actual=CompareLine(value=actual, description=f"got type {type(actual)}"),
            error=True,
        )

    if isinstance(expected, Unsorted):
        return await compare_unsorted_lists_v2(expected, actual, partial_content, context)

    result = CompareResultComplex[CompareListItem]()

    for i in range(0, max(len(expected), len(actual))):
        compare_response = await complex_compare_v2(
            expected[i] if i < len(expected) else Missing,
            actual[i] if i < len(actual) else Missing,
            partial_content,
            context,
        )

        if isinstance(compare_response, CompareResultSimple):
            result.items.append(
                CompareListItemSimple(
                    index=i,
                    error=compare_response.error,
                    expected=compare_response.expected,
                    actual=compare_response.actual,
                )
            )
        elif isinstance(compare_response, CompareResultComplex):
            result.items.append(
                CompareListItemComplex(
                    index=i,
                    error=compare_response.error,
                    items=compare_response.items,
                )
            )

    return result


async def compare_specific_types(expected: Any, actual: Any) -> CompareResult:
    """
    Compare specific types of results.
    """

    # Datetime must be first, as datetime is also instance of date.
    if isinstance(expected, datetime):
        try:
            result = await evaluate_jinja("{{ value | datetime == expected }}", {"value": actual, "expected": expected})
            return CompareResultSimple(
                expected=CompareLine(value=expected),
                actual=CompareLine(value=actual),
                error=not result,
            )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            return CompareResultSimple(
                error=True,
                expected=CompareLine(value=expected),
                actual=CompareLine(value=actual, description=f"Error evaluating date comparison: {exc!s}"),
            )

    if isinstance(expected, date):
        try:
            result = await evaluate_jinja("{{ value | date == expected }}", {"value": actual, "expected": expected})
            return CompareResultSimple(
                expected=CompareLine(value=expected),
                actual=CompareLine(value=actual),
                error=not result,
            )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            return CompareResultSimple(
                error=True,
                expected=CompareLine(value=expected),
                actual=CompareLine(value=actual, description=f"Error evaluating date comparison: {exc!s}"),
            )

    raise ValueError(f"Unsupported expected type: {type(expected).__name__}")


async def complex_compare_v2(
    expected: Any,
    actual: Any,
    partial_content: bool,
    context: dict[str, Any],
) -> CompareResult:
    """
    Compare two structures, recursively.
    """

    # pylint: disable=too-many-return-statements

    original_expected = expected
    if isinstance(expected, str) and is_template_string(expected):
        try:
            expected = await evaluate_jinja(
                expected,
                {
                    **context,
                    "value": actual,
                },
            )

            if expected is False:
                return CompareResultSimple(
                    error=True,
                    expected=CompareLine(value=original_expected, description="Template evaluated to False."),
                    actual=CompareLine(value=actual),
                )

            if expected is True:
                return CompareResultSimple(
                    expected=CompareLine(value=original_expected, description="Template evaluated to True."),
                    actual=CompareLine(value=actual),
                )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            return CompareResultSimple(
                error=True,
                expected=CompareLine(value=original_expected, description=f"Error evaluating template: {exc!s}"),
                actual=CompareLine(value=actual),
            )

    if expected is Missing:
        return CompareResultSimple(
            error=True, expected=None, actual=CompareLine(value=actual, description="excessive item in actual list")
        )

    if actual is Missing:
        return CompareResultSimple(
            error=True, expected=CompareLine(value=expected, description="missing item in actual list"), actual=None
        )

    if is_simple_value(expected):
        try:
            assert_that(actual).is_equal_to(expected)
            error = False
            description = None
        except Exception as exc:  # pylint: disable=broad-exception-caught
            error = True
            description = str(exc)

        return CompareResultSimple(
            expected=CompareLine(
                value=original_expected,
                description=f"evaluated to {expected!r} (type: {type(expected).__name__})"
                if expected != original_expected
                else None,
            ),
            actual=CompareLine(value=actual, description=description),
            error=error,
        )

    if isinstance(expected, dict):
        return await compare_dicts_v2(expected, actual, partial_content, context)

    if isinstance(expected, Sequence) and not isinstance(expected, (str, bytes)):
        return await compare_lists_v2(expected, actual, partial_content, context)

    return await compare_specific_types(expected, actual)


async def compare_dicts(
    expected: dict[str, Any], actual: Any, partial_content: bool, context: dict[str, Any], path: str = ""
) -> list[str]:
    """Compare two dictionaries, recursively."""

    errors: list[str] = []
    prefix = prefix_from_path(path)

    if not isinstance(actual, dict):
        errors.append(f"{prefix}Expected dict, got {type(actual)}")
        return errors

    for key, value in expected.items():
        if key not in actual:
            errors.append(f"{prefix}Key {key} not found in actual dict")
            continue

        errors.extend(
            await complex_compare(
                value,
                actual[key],
                partial_content,
                context,
                f"{path}.{key}" if path else key,
            )
        )

    if not partial_content:
        for key in actual:
            if key not in expected:
                errors.append(f"{prefix}Key {key} was not expected.")

    return errors


async def compare_unsorted_lists(
    expected: Unsorted,
    actual: Sequence[Any],
    partial_content: bool,
    context: dict[str, Any],
    path: str = "",
) -> list[str]:
    """Compare two lists, without considering the order of items. Tries to find minimal differences."""

    errors: list[str] = []
    prefix = prefix_from_path(path)

    actual = list(actual)
    for i, value in enumerate(expected):
        min_errors = None
        min_idx = None

        if not actual:
            # If actual is empty, we cannot find a match.
            errors.append(f"{prefix}Expected item {value!r} not found in actual list.")
            continue

        for j, actual_value in enumerate(actual):
            err = await complex_compare(value, actual_value, partial_content, context, f"{path}[{i}]")
            if min_errors is None or len(err) < len(min_errors):
                min_errors = err
                min_idx = j

            if not err:
                # "consume" item that matches expected.
                actual.pop(j)
                break
        else:
            if min_idx is not None:
                actual.pop(min_idx)

        if min_errors:
            errors.extend(min_errors)

    if not isinstance(expected, PartialList):
        if actual:
            errors.append(f"{prefix}Actual list contains unexpected items: {actual}")

    return errors


async def compare_lists(
    expected: Sequence[Any],
    actual: Any,
    partial_content: bool,
    context: dict[str, Any],
    path: str = "",
) -> list[str]:
    """Compare two lists, recursively."""

    errors: list[str] = []
    prefix = prefix_from_path(path)

    if not isinstance(actual, Sequence) and not isinstance(expected, (str, bytes)):
        errors.append(f"{prefix}Expected list, got {type(actual)}")
        return errors

    if len(expected) != len(actual) and not isinstance(expected, PartialList):
        errors.append(f"{prefix}Expected list of length {len(expected)}, got {len(actual)}")
        return errors

    if isinstance(expected, Unsorted):
        errors.extend(await compare_unsorted_lists(expected, actual, partial_content, context, path))

    else:
        for i, value in enumerate(expected):
            errors.extend(await complex_compare(value, actual[i], partial_content, context, f"{path}[{i}]"))

    return errors


async def complex_compare(
    expected: Any,
    actual: Any,
    partial_content: bool,
    context: dict[str, Any],
    path: str = "",
) -> list[str]:
    """
    Compare two structures, recursively. Supports comparing all the special data types from the models submodule.
    :param expected: Expected response with optional advanced validation models.
    :param actual: Actual response received from the REST API.
    :param partial_content: Validate only partial content for dicts. That means, only keys that are present in the expected
      response are validated, the rest is ignored.
    :param context: Context for Jinja evaluation. Used to evaluate Jinja expressions in the expected response.
    :param path: Path to the currently compared item. Used to construct meaningful error messages. You don't need to pass
      this, it's used internally.
    :return:  List of error messages, if comparison was not successful. Empty list if expected equals actual.
    """
    errors: list[str] = []

    prefix = prefix_from_path(path)

    if isinstance(expected, str) and is_template_string(expected):
        original_expected = expected
        try:
            expected = await evaluate_jinja(
                expected,
                {
                    **context,
                    "value": actual,
                },
            )

            if expected is False:
                return [f"{prefix}Template {original_expected!r} evaluated as False, with actual value {actual!r}"]

            if expected is True:
                return []
        except AssertionError:
            raise
        except Exception as exc:  # pylint: disable=broad-except
            return [f"{prefix}Error evaluating template {original_expected!r}: {exc!s}"]

    if isinstance(expected, dict):
        errors.extend(await compare_dicts(expected, actual, partial_content, context, path))

    elif isinstance(expected, Sequence) and not isinstance(expected, (str, bytes)):
        errors.extend(await compare_lists(expected, actual, partial_content, context, path))

    else:
        try:
            if not isinstance(actual, (int, float)) or not isinstance(expected, (int, float)):
                # For non-numeric types, also check the type.
                assert_that(actual).is_type_of(type(expected))

            assert_that(actual).is_equal_to(expected)
        except AssertionError as exc:
            errors.append(f"{prefix}{exc!s}")

    return errors


async def assert_complex(
    expected: Any,
    actual: Any,
    partial_content: bool,
    context: dict[str, Any],
) -> None:
    """
    Assert that two structures are equal, using complex comparison.
    :param expected: Expected response with optional advanced validation models.
    :param actual: Actual response received from the REST API.
    :param partial_content: Validate only partial content for dicts. That means, only keys that are present in the expected
      response are validated, the rest is ignored.
    :param context: Context for Jinja evaluation. Used to evaluate Jinja expressions in the expected response.
    """
    result = await complex_compare_v2(expected, actual, partial_content, context)
    if result.total_errors > 0:
        raise AssertionError(result.format())
