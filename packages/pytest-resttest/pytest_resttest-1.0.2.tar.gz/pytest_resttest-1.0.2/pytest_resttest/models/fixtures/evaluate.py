from collections.abc import AsyncGenerator
from contextlib import AsyncExitStack
from typing import Any

from pydantic import Field

from pytest_resttest.jinja import evaluate_jinja
from pytest_resttest.models.base import BaseModel
from pytest_resttest.models.fixture import FixtureType
from pytest_resttest.models.suite import Suite


class Evaluate(BaseModel):
    """
    Evaluate fixture, same as Evaluate test but without result comparison.
    """

    template: str = Field(description="Template to be evaluated.")


async def evaluate_fixture(
    suite: Suite,
    exit_stack: AsyncExitStack,
    context: dict[str, Any],
    params: Evaluate,
) -> AsyncGenerator[Any, Any]:
    """
    Fixture to evaluate any template before test runs. Intended usage is to pre-fill storedResult with values for tests.
    """
    # pylint: disable=unused-argument

    await evaluate_jinja(params.template, context)
    yield


Suite.register_fixture("Evaluate", FixtureType.SUITE, evaluate_fixture, Evaluate)
