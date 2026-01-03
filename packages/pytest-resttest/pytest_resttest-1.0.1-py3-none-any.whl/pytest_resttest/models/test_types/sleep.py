import asyncio
from contextlib import AsyncExitStack
from typing import Any

from pydantic import Field

from pytest_resttest.jinja import evaluate_jinja
from pytest_resttest.models.jinja import Jinja
from pytest_resttest.models.suite import Suite
from pytest_resttest.models.test_types.base import BaseTest


class SleepTest(BaseTest):
    """
    Test type that sleeps for a specified duration. Always succeeds.
    """

    sleep: Jinja[float] = Field(
        gt=0.0,
    )

    async def __call__(self, suite: Suite, exit_stack: AsyncExitStack, context: dict[str, Any]) -> None:
        """
        Sleep for the specified duration.

        Args:
            suite (Suite): The test suite instance.
            exit_stack (AsyncExitStack): The async exit stack for cleanup.
            context (dict[str, Any]): Context dictionary for passing data between tests.
        """
        sleep = await evaluate_jinja(self.sleep, context) if isinstance(self.sleep, str) else self.sleep

        if not isinstance(sleep, (int, float)):
            raise TypeError(f"Expected sleep duration to be int or float, got {type(sleep).__name__}")

        await asyncio.sleep(sleep)


Suite.register_test_type(SleepTest)


__all__ = ["SleepTest"]
