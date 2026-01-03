from collections.abc import AsyncGenerator
from contextlib import AsyncExitStack
from enum import StrEnum
from typing import Any

from pydantic import Field

from pytest_resttest.models.base import BaseModel
from pytest_resttest.models.fixture import FixtureType
from pytest_resttest.models.jinja import Jinja
from pytest_resttest.models.suite import Suite
from pytest_resttest.models.test_types.db import DatabaseQuery, DatabaseTarget, Query


class CleanupMode(StrEnum):
    """When to run the cleanup queries."""

    BEFORE = "before"  # Run before the test suite
    AFTER = "after"  # Run after the test suite
    BOTH = "both"  # Run before and after the test suite


class CleanQueries(BaseModel):
    """
    Model for defining cleanup queries to run before or after a test suite.
    """

    target: DatabaseTarget
    queries: list[Jinja[str] | Query] = Field(default=[])
    mode: CleanupMode = CleanupMode.BEFORE


async def clean_db(
    suite: Suite,
    exit_stack: AsyncExitStack,
    context: dict[str, Any],
    params: CleanQueries,
) -> AsyncGenerator[Any, Any]:
    """
    Fixture to clean the database before running tests.
    This fixture should be used at the suite level.
    """
    query = DatabaseQuery(name="Cleanup database", target=params.target, queries=params.queries, description=None)

    if params.mode in (CleanupMode.BEFORE, CleanupMode.BOTH):
        await query(suite, exit_stack, context)

    # Yield control back to the test runner
    yield

    if params.mode in (CleanupMode.AFTER, CleanupMode.BOTH):
        await query(suite, exit_stack, context)


Suite.register_fixture("CleanDB", FixtureType.SUITE, clean_db, CleanQueries)
