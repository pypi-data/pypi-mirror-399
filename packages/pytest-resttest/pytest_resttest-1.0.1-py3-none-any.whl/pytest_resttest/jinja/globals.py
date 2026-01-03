import random
import string
from collections.abc import Sequence
from datetime import UTC, date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from assertpy import assert_that

from pytest_resttest.jinja.env import JINJA_ENV
from pytest_resttest.jinja.filters import filter_store


def global_random(alphabet: Sequence[str], length: int = 1) -> str:
    """
    Generates a random string of specified length using the provided alphabet.
    If no alphabet is provided, it defaults to lowercase ASCII letters.
    """
    return "".join(random.choice(alphabet) for _ in range(length))  # noqa: S311


def global_now() -> datetime:
    """
    Returns the current UTC datetime.
    """
    return datetime.now(UTC)


JINJA_ENV.globals.update(
    {
        "datetime": datetime,
        "date": date,
        "time": time,
        "timedelta": timedelta,
        "timezone": timezone,
        "ZoneInfo": ZoneInfo,
        "now": global_now,
        "store": filter_store,
        "string": string,
        "random": global_random,
        "assert_that": assert_that,
    }
)
