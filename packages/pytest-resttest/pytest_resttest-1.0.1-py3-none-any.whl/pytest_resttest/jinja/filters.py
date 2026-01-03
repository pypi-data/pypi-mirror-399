import re
from datetime import date, datetime, time, timedelta
from typing import Any, overload
from urllib.parse import SplitResult, parse_qs, parse_qsl, urlencode, urlsplit

import isodate
from jinja2.exceptions import TemplateRuntimeError
from jinja2.runtime import Context
from jinja2.utils import pass_context  # type: ignore[attr-defined]

from pytest_resttest.compare.partial import PartialList, Unsorted
from pytest_resttest.jinja.env import JINJA_ENV


def filter_datetime(value: Any) -> datetime:
    """
    Jinja2 filter to convert a value to a datetime object.
    """
    if isinstance(value, datetime):
        return value

    return isodate.isodatetime.parse_datetime(value)


def filter_date(value: Any) -> date:
    """
    Jinja2 filter to convert a value to a date object.
    """
    if isinstance(value, date):
        return value

    return isodate.isodates.parse_date(value)


def filter_time(value: Any) -> time:
    """
    Jinja2 filter to convert a value to a time object.
    """
    if isinstance(value, time):
        return value

    return isodate.isotime.parse_time(value)


def filter_timedelta(value: Any) -> timedelta:
    """
    Jinja2 filter to convert a value to a timedelta object.
    """
    if isinstance(value, timedelta):
        return value

    if isinstance(value, (int, float)):
        return timedelta(seconds=value)

    duration = isodate.parse_duration(value, as_timedelta_if_possible=True)
    if not isinstance(duration, timedelta):
        raise ValueError(f"Invalid value for timedelta: {value}")

    return duration


def filter_regex_match(value: Any, pattern: str) -> bool:
    """
    Jinja2 filter to check if a value matches a regex pattern.
    """
    return bool(re.match(pattern, str(value)))


def filter_regex_search(value: Any, pattern: str) -> bool:
    """
    Jinja2 filter to check if a value contains a regex pattern.
    """
    return bool(re.search(pattern, str(value)))


@pass_context
def filter_store(context: Context, value: Any, name: str) -> Any:
    """
    Jinja2 filter to store a value in the context's storedResult dictionary.
    Returns the value without modification.
    """

    if "storedResult" not in context:
        raise TemplateRuntimeError("No storedResult available in the context.")

    context["storedResult"][name] = value
    return value


def filter_unsorted(value: Any) -> Any:
    """
    Jinja2 filter to return the value without modification.
    This is used to ensure that the value is not sorted.
    """
    return Unsorted(list(value))


def filter_partial_list(value: Any) -> Any:
    """
    Jinja2 filter to return the value as a partial list.
    This is used to ensure that the value can contain additional items.
    """
    if isinstance(value, Unsorted):
        return value
    return PartialList(list(value))


def filter_isoformat(value: Any) -> str:
    """
    Jinja2 filter to convert a value to an ISO 8601 formatted string.
    """

    if isinstance(value, (datetime, date, time)):
        return value.isoformat()

    raise ValueError(f"Value {value} cannot be converted to ISO format.")


def filter_url(value: Any) -> SplitResult:
    """
    Jinja2 filter to parse a URL and return its components.
    """

    return urlsplit(value)


@overload
def filter_qs(value: dict[str, Any]) -> str: ...


@overload
def filter_qs(value: str) -> dict[str, Any]: ...


def filter_qs(value: Any) -> str | dict[str, Any]:
    """
    Jinja2 filter to convert a dictionary to a query string.
    """

    if isinstance(value, dict):
        return urlencode(value)

    if isinstance(value, SplitResult):
        value = value.query

    if isinstance(value, str):
        # If the value is a string, we assume it's already a query string.
        return parse_qs(value, strict_parsing=True, errors="strict")

    raise ValueError(f"Value {value} cannot be converted to query string.")


@overload
def filter_qsl(value: list[tuple[str, Any]]) -> str: ...


@overload
def filter_qsl(value: str) -> list[tuple[str, Any]]: ...


def filter_qsl(value: Any) -> str | list[tuple[str, Any]]:
    """
    Jinja2 filter to convert a list of key-value pairs to a query string.
    """

    if isinstance(value, list):
        return urlencode(value)

    if isinstance(value, SplitResult):
        value = value.query

    if isinstance(value, str):
        # If the value is a string, we assume it's already a query string.
        return parse_qsl(value, strict_parsing=True, errors="strict")

    raise ValueError(f"Value {value} cannot be converted to query string.")


JINJA_ENV.filters.update(
    {
        "datetime": filter_datetime,
        "date": filter_date,
        "time": filter_time,
        "timedelta": filter_timedelta,
        "isoformat": filter_isoformat,
        "regex_match": filter_regex_match,
        "regex_search": filter_regex_search,
        "store": filter_store,
        "unsorted": filter_unsorted,
        "partial_list": filter_partial_list,
        "url": filter_url,
        "qs": filter_qs,
        "qsl": filter_qsl,
    }
)
