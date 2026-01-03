from collections.abc import Iterable
from datetime import date, datetime, time, timedelta
from typing import Any

from pytest_resttest.jinja.env import JINJA_ENV
from pytest_resttest.jinja.filters import (
    filter_date,
    filter_datetime,
    filter_regex_match,
    filter_regex_search,
    filter_time,
    filter_timedelta,
)


def test_is_datetime(value: Any) -> bool:
    """
    jinja2 test to check if a value is a datetime object.
    """
    if isinstance(value, str):
        try:
            value = filter_datetime(value)
        except ValueError:
            return False

    return isinstance(value, datetime)


def test_is_date(value: Any) -> bool:
    """
    jinja2 test to check if a value is a date object.
    """
    if isinstance(value, str):
        try:
            value = filter_date(value)
        except ValueError:
            return False

    return isinstance(value, date)


def test_is_time(value: Any) -> bool:
    """
    jinja2 test to check if a value is a time object.
    """
    if isinstance(value, str):
        try:
            value = filter_time(value)
        except ValueError:
            return False

    return isinstance(value, time)


def test_is_timedelta(value: Any) -> bool:
    """
    jinja2 test to check if a value is a timedelta object.
    """
    if isinstance(value, str):
        try:
            value = filter_timedelta(value)
        except ValueError:
            return False

    return isinstance(value, timedelta)


def test_in_last(value: datetime | str, **kwargs: Any) -> bool:
    """
    jinja2 test to check if a datetime value is within given timedelta
    """
    if isinstance(value, str):
        value = filter_datetime(value)

    if not isinstance(value, datetime):
        raise TypeError("value must be a datetime object")

    diff = (datetime.now(tz=value.tzinfo) - value).total_seconds()
    return diff <= timedelta(**kwargs).total_seconds()


def test_tzaware(value: Any) -> bool:
    """
    jinja2 test to check if a value is timezone-aware datetime.
    """
    if not isinstance(value, datetime):
        value = filter_datetime(value)

    return value.tzinfo is not None


def test_is_array(value: Any) -> bool:
    """
    jinja2 test to check if a value is an array (list).
    """
    return isinstance(value, Iterable) and not isinstance(value, (str, bytes))


JINJA_ENV.tests.update(
    {
        "datetime": test_is_datetime,
        "date": test_is_date,
        "time": test_is_time,
        "timedelta": test_is_timedelta,
        "in_last": test_in_last,
        "tzaware": test_tzaware,
        "array": test_is_array,
        "regex_match": filter_regex_match,
        "regex_search": filter_regex_search,
    }
)
