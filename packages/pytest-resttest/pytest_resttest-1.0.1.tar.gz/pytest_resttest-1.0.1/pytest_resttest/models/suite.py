from __future__ import annotations

import os
import re
from contextlib import AsyncExitStack, asynccontextmanager
from types import TracebackType
from typing import TYPE_CHECKING, Annotated, Any, ClassVar, Literal, Self, TypeVar, cast, overload

from pydantic import BeforeValidator, Field, SerializeAsAny, field_validator, model_validator

from pytest_resttest.lib.indent import indent
from pytest_resttest.lib.stored_result import StoredResult
from pytest_resttest.lib.yaml import YAML
from pytest_resttest.models.base import BaseModel
from pytest_resttest.models.exceptions import SuiteLoadError
from pytest_resttest.models.fixture import (
    Fixture,
    FixtureParamsT_contra,
    FixtureType,
    FixtureWithoutParams,
    FixtureWithParams,
    ParametrizedFixture,
    SuiteLevelFixture,
    SuiteLevelFixtureWithParams,
    TestLevelFixture,
    TestLevelFixtureWithParams,
)
from pytest_resttest.models.http_types import Cookies, Headers, HttpTarget
from pytest_resttest.reporter.base import ReporterInterface

if TYPE_CHECKING:
    from pytest_resttest.models.test_types.base import BaseTest


class SuiteDefaults(BaseModel):
    """Default values for the suite, used when not specified in the test itself."""

    target: HttpTarget | None = None
    headers: Headers | None = None
    cookies: Cookies | None = None


def validate_test_types(value: Any) -> Any:
    """
    Validate that all tests in the suite are of registered types.
    """
    if not isinstance(value, dict):
        return value

    errors: dict[str, str] = {}

    for test_type in Suite.__test_types__:
        try:
            return test_type.model_validate(value)
        except Exception as exc:  # pylint: disable=broad-except
            errors[test_type.__name__] = str(exc)

    out: list[str] = ["Unable to determine test type. Validation errors:"]

    for model_name, model_errors in errors.items():
        out.append(f"    {model_name}\n{indent(model_errors, '        ')}")

    raise ValueError("\n".join(out))


def validate_fixture(value: dict[str, Any] | Any) -> Any:
    """
    Validate that the fixture is registered in the suite.
    """
    if isinstance(value, str):
        value = {
            "name": value,
            "params": cast(Any, None),
        }

    if not isinstance(value, dict):
        return value

    fixture_name = value.get("name")

    if fixture_name not in Suite.__fixture_types__:
        raise ValueError(f"Fixture '{fixture_name}' is not registered in the suite.")

    params_model = Suite.__fixture_types__[fixture_name][2]

    if params_model is not None:
        value["params"] = params_model.model_validate(value.get("params"))

    return ParametrizedFixture.model_validate(value)


class SuiteReference(BaseModel):
    """
    Model representing a reference to another test suite file.
    """

    file: str

    @field_validator("file", mode="after")
    @classmethod
    def validate_file_exists(cls, value: str) -> str:
        """
        Validate that the file exists.
        """
        return os.path.realpath(value, strict=True)


class PartialSuite(BaseModel):
    """
    Represents a collection of tests that can be executed together. This class does not check it's consistency, as it can be
    merged to another suite, which eventually forms a complete test suite.
    """

    name: str
    fixtures: list[Annotated[str | ParametrizedFixture, BeforeValidator(validate_fixture)]] = Field(default=[])
    defaults: SuiteDefaults = SuiteDefaults()
    tests: list[Annotated[SerializeAsAny[BaseTest], BeforeValidator(validate_test_types)]] = Field(default=[])

    include: list[SuiteReference | str] | str = None

    @property
    def safe_name(self) -> str:
        """
        Returns a safe name for the test, suitable for use in URLs or filenames.
        Replaces spaces with underscores and removes any non-alphanumeric characters.
        """
        return re.sub(r"[^\w]", "_", self.name)

    @classmethod
    def _process_include(cls, include: SuiteReference) -> PartialSuite:
        # This method will be usefull when other types of includes are supported in the future.

        return cls.load_suite_from_file(include.file, PartialSuite)

    @overload
    @staticmethod
    def load_suite_from_file(filename: str, suite_class: None = None) -> Suite: ...

    @overload
    @staticmethod
    def load_suite_from_file(filename: str, suite_class: type[SuiteT]) -> SuiteT: ...

    @staticmethod
    def load_suite_from_file(filename: str, suite_class: type[SuiteT] | type[Suite] | None = None) -> SuiteT | Suite:
        """
        Load a test suite from a YAML file.
        :param filename: Filename of the YAML file containing the test suite.
        :param suite_class: Optional class to use for the suite. If not provided, defaults to `Suite`.
        :return: An instance of the suite class with the loaded data.
        :raises Exception: When the suite cannot be loaded or validated.
        """

        try:
            if suite_class is None:
                suite_class = Suite

            current_cwd = os.getcwd()
            os.chdir(os.path.dirname(filename))
            try:
                with open(filename, encoding="utf-8") as f:
                    data = YAML().load(f)
                    return suite_class.model_validate(data)
            finally:
                os.chdir(current_cwd)
        except Exception as exc:
            raise SuiteLoadError(f"While loading {filename}:\n{exc!s}") from None

    def _merge_suite(self, to_be_merged: PartialSuite) -> None:
        # Merge the included suite into the current suite.
        if to_be_merged.fixtures:
            self.fixtures = [*to_be_merged.fixtures, *self.fixtures]

        if to_be_merged.tests:
            self.tests = [*to_be_merged.tests, *self.tests]

        if to_be_merged.defaults:
            self.defaults = SuiteDefaults.model_validate(
                to_be_merged.defaults.model_dump(by_alias=True, exclude_unset=True)
                | self.defaults.model_dump(by_alias=True, exclude_unset=True)
            )

    @model_validator(mode="after")
    def resolve_includes(self) -> Self:
        """
        Resolve any included suites and merge their tests and fixtures into this suite.
        """
        if not self.include:
            return self

        if isinstance(self.include, str):
            self.include = [self.include]

        # The includes are processed in reverse order, so that the last included suite has the highest priority. This also
        # ensures that the first suite's tests and fixtures are evaluated first, second second and so on. Tests and fixtures
        # defined in the test suite itself will be executed last.
        for include in reversed(self.include):
            if isinstance(include, str):
                include_suite = SuiteReference(file=include)
            else:
                include_suite = include

            included_suite = self._process_include(include_suite)
            self._merge_suite(included_suite)

        return self


class Suite(PartialSuite):
    """
    Represents a collection of tests that can be executed together.
    """

    __test_types__: ClassVar[set[type[BaseTest]]] = set()
    __fixture_types__: ClassVar[dict[str, tuple[FixtureType, Fixture[Any], type[BaseModel] | None]]] = {}

    @model_validator(mode="after")
    def ensure_target_is_specified(self) -> Self:
        """Validate there is a target specified for all the HTTP tests."""

        from pytest_resttest.models.test_types.http import HttpTestBase  # pylint: disable=import-outside-toplevel, cyclic-import

        for test in self.tests:
            # Default target is for HTTP tests only.
            if not isinstance(test, HttpTestBase):
                continue

            if not test.target and not self.defaults.target:
                raise ValueError("Missing Suite defaults.target field for tests, or target for each test.")

        return self

    @classmethod
    def register_test_type(cls, test_type: type[BaseTest]) -> None:
        """Register a new test type to be used in the suite."""
        cls.__test_types__.add(test_type)

    @overload
    @classmethod
    def register_fixture(
        cls,
        fixture_name: str,
        fixture_type: Literal[FixtureType.SUITE],
        fixture: SuiteLevelFixture,
    ) -> None: ...

    @overload
    @classmethod
    def register_fixture(
        cls,
        fixture_name: str,
        fixture_type: Literal[FixtureType.SUITE],
        fixture: SuiteLevelFixtureWithParams[FixtureParamsT_contra],
        params_model: type[FixtureParamsT_contra],
    ) -> None: ...

    @overload
    @classmethod
    def register_fixture(
        cls,
        fixture_name: str,
        fixture_type: Literal[FixtureType.TEST],
        fixture: TestLevelFixture,
    ) -> None: ...

    @overload
    @classmethod
    def register_fixture(
        cls,
        fixture_name: str,
        fixture_type: Literal[FixtureType.TEST],
        fixture: TestLevelFixtureWithParams[FixtureParamsT_contra],
        params_model: type[FixtureParamsT_contra],
    ) -> None: ...

    @classmethod
    def register_fixture(
        cls,
        fixture_name: str,
        fixture_type: FixtureType,
        fixture: FixtureWithoutParams | FixtureWithParams[FixtureParamsT_contra],
        params_model: type[FixtureParamsT_contra] | None = None,
    ) -> None:
        """Register a new fixture to be used in the suite."""
        cls.__fixture_types__[fixture_name] = (fixture_type, fixture, params_model)  # type: ignore[assignment]

    async def setup(self) -> tuple[AsyncExitStack, dict[str, Any]]:
        """Test suite setup."""

        # as we need to return the stack when everything is fine.
        stack = await AsyncExitStack().__aenter__()  # pylint: disable=unnecessary-dunder-call

        try:
            suite_level_fixture_data: dict[str, Any] = {}

            context = {
                "suite": self,
                "fixtures": suite_level_fixture_data,
                "storedResult": StoredResult(),
            }

            # Run all suite-level fixtures
            for fixture in cast(list[ParametrizedFixture], self.fixtures):
                fixture_type, fixture_callable, fixture_params_model = self.__class__.__fixture_types__[fixture.name]

                if fixture_type == FixtureType.SUITE and fixture_params_model is not None:
                    fixture_params = fixture.params or BaseModel()
                    suite_level_fixture_data[fixture.name] = await stack.enter_async_context(
                        asynccontextmanager(fixture_callable)(self, stack, context, fixture_params)
                    )
                elif fixture_type == FixtureType.SUITE:
                    suite_level_fixture_data[fixture.name] = await stack.enter_async_context(
                        asynccontextmanager(fixture_callable)(self, stack, context)
                    )

            return stack, context
        except Exception as exc:
            await stack.__aexit__(type(exc), exc, exc.__traceback__)
            raise

    async def teardown(
        self,
        stack: AsyncExitStack,
        exc_type: type[BaseException] | None = None,
        exc: BaseException | None = None,
        tb: TracebackType | None = None,
    ) -> None:
        # pylint: disable=no-self-use  # as we don't know the future, and this is a public API.
        """Test suite teardown."""

        await stack.__aexit__(exc_type, exc, tb)

    async def run_test(self, test: BaseTest, stack: AsyncExitStack, context: dict[str, Any]) -> None:
        """
        Run a single test with the provided context and exit stack.
        """
        test_level_fixture_data: dict[str, Any] = {
            **context.get("fixtures", {}),
        }

        test_context = {
            **context,
            "test": test,
            "fixtures": test_level_fixture_data,
        }

        async with AsyncExitStack() as test_stack:
            # Run all test-level fixtures
            for fixture in cast(list[ParametrizedFixture], self.fixtures):
                fixture_callable = self.__class__.__fixture_types__[fixture.name][0]

                if isinstance(fixture_callable, TestLevelFixture):
                    test_level_fixture_data[fixture.name] = await stack.enter_async_context(
                        asynccontextmanager(fixture_callable)(self, test, test_stack, test_context)
                    )
                elif isinstance(fixture_callable, TestLevelFixtureWithParams):
                    fixture_params = fixture.params or BaseModel()
                    test_level_fixture_data[fixture.name] = await stack.enter_async_context(
                        asynccontextmanager(fixture_callable)(self, test, test_stack, test_context, fixture_params)
                    )

            await test(self, stack, test_context)

    async def __call__(self, reporter: ReporterInterface) -> None:
        """
        Run all tests in the suite and report their results using the provided reporter. This is called only if the suite
        is executed outside the pytest environment.
        """

        reporter.report_suite_start(self)
        stack, context = await self.setup()

        for test in self.tests:
            reporter.report_test_start(self, test)

            try:
                if test.skip:
                    reporter.report_test_skip(self, test)
                else:
                    await self.run_test(test, stack, context)
                    reporter.report_test_pass(self, test)

            except Exception as exc:  # pylint: disable=broad-exception-caught
                reporter.report_test_fail(self, test, exc)

            finally:
                reporter.report_test_end(self, test)

        reporter.report_suite_end(self)


SuiteT = TypeVar("SuiteT", bound=PartialSuite, default=Suite)
