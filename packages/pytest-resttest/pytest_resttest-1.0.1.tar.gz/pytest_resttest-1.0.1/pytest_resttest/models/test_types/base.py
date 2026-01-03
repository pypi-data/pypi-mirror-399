from __future__ import annotations

import re
from abc import abstractmethod
from contextlib import AsyncExitStack
from typing import TYPE_CHECKING, Any

from pydantic import Field

from pytest_resttest.models.base import BaseModel

if TYPE_CHECKING:
    from pytest_resttest.models.suite import Suite


class BaseTest(BaseModel):
    """Base class for all test types in pytest-resttest."""

    name: str
    desc: str | None = Field(None, alias="description")
    skip: bool = False

    @abstractmethod
    async def __call__(self, suite: Suite, exit_stack: AsyncExitStack, context: dict[str, Any]) -> None:
        """Execute the test logic. Raise an exception if the test should be reported as failed."""

    @property
    def safe_name(self) -> str:
        """
        Returns a safe name for the test, suitable for use in URLs or filenames.
        Replaces spaces with underscores and removes any non-alphanumeric characters.
        """
        return re.sub(r"[^\w]", "_", self.name)
