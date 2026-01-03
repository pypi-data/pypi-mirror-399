from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import AsyncExitStack
from enum import Enum, auto
from typing import (
    TYPE_CHECKING,
    Any,
    Protocol,
    TypeVar,
    runtime_checkable,
)

from pydantic import BaseModel as PydanticBaseModel
from pydantic import SerializeAsAny

from pytest_resttest.models.base import BaseModel

if TYPE_CHECKING:
    from pytest_resttest.models.suite import Suite
    from pytest_resttest.models.test_types.base import BaseTest


class FixtureType(Enum):
    """Type of fixture - whether it is a suite-level or test-level fixture."""

    SUITE = auto()
    TEST = auto()


FixtureParamsT_contra = TypeVar("FixtureParamsT_contra", bound=PydanticBaseModel, contravariant=True)


@runtime_checkable
class SuiteLevelFixture(Protocol):
    """Protocol for a fixture that is applied at the suite level."""

    def __call__(self, suite: Suite, exit_stack: AsyncExitStack, context: dict[str, Any]) -> AsyncGenerator[Any, Any]: ...


@runtime_checkable
class SuiteLevelFixtureWithParams(Protocol[FixtureParamsT_contra]):
    """Protocol for a fixture that is applied at the suite level with parameters."""

    def __call__(
        self,
        suite: Suite,
        exit_stack: AsyncExitStack,
        context: dict[str, Any],
        params: FixtureParamsT_contra,
    ) -> AsyncGenerator[Any, Any]: ...


@runtime_checkable
class TestLevelFixture(Protocol):
    """Protocol for a fixture that is applied at the test level."""

    def __call__(
        self,
        suite: Suite,
        test: BaseTest,
        exit_stack: AsyncExitStack,
        context: dict[str, Any],
    ) -> AsyncGenerator[Any, Any]: ...


@runtime_checkable
class TestLevelFixtureWithParams(Protocol[FixtureParamsT_contra]):
    """Protocol for a fixture that is applied at the test level with parameters."""

    def __call__(
        self,
        suite: Suite,
        test: BaseTest,
        exit_stack: AsyncExitStack,
        context: dict[str, Any],
        params: FixtureParamsT_contra,
    ) -> AsyncGenerator[Any, Any]: ...


type Fixture[FixtureParamsT_contra: PydanticBaseModel] = (
    SuiteLevelFixture
    | SuiteLevelFixtureWithParams[FixtureParamsT_contra]
    | TestLevelFixture
    | TestLevelFixtureWithParams[FixtureParamsT_contra]
)
type FixtureWithoutParams = SuiteLevelFixture | TestLevelFixture
type FixtureWithParams[FixtureParamsT_contra: PydanticBaseModel] = (
    SuiteLevelFixtureWithParams[FixtureParamsT_contra] | TestLevelFixtureWithParams[FixtureParamsT_contra]
)


class ParametrizedFixture(BaseModel):
    """Model for specifying a fixture in YAML test suite."""

    name: str
    params: SerializeAsAny[BaseModel] | None = None
