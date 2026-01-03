from __future__ import annotations

import asyncio
import os
from collections.abc import Generator
from contextlib import AsyncExitStack
from pathlib import PosixPath
from typing import Any, cast

import pytest
from _pytest._code.code import ExceptionInfo, TerminalRepr, TracebackStyle

from pytest_resttest.models import Suite
from pytest_resttest.models.exceptions import RestAssertionError, TestMalformed
from pytest_resttest.models.test_types.base import BaseTest


class YamlFile(pytest.File):
    """
    Represents a pytest node for a YAML test suite.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.rest_suite: Suite | None = None
        self.rest_loop = asyncio.get_event_loop()
        self.rest_exit_stack: AsyncExitStack | None = None
        self.rest_context: dict[str, Any] = {}

    def collect(self) -> Generator[YamlTest]:
        """
        Collect YAML files.
        """

        self.rest_suite = Suite.load_suite_from_file(str(self.path))

        for spec in self.rest_suite.tests:
            yield YamlTest.from_parent(
                self,
                name=spec.safe_name,
                suite=self.rest_suite,
                spec=spec,
            )

    def setup(self) -> None:
        """
        Setup the yaml file node.
        """

        self.rest_exit_stack, self.rest_context = self.rest_loop.run_until_complete(self.rest_suite.setup())

    def teardown(self) -> None:
        """
        Teardown the yaml file node.
        """

        self.rest_loop.run_until_complete(self.rest_suite.teardown(self.rest_exit_stack))

    def reportinfo(self) -> tuple[os.PathLike[str] | str, int | None, str]:
        """
        Return the file path and the number of tests.
        """

        return self.path, 0, self.rest_suite.safe_name


class YamlTest(pytest.Item):
    """
    Represents a single test case within a YAML test suite.
    """

    def __init__(
        self,
        *args: Any,
        suite: Suite,
        spec: BaseTest,
        lineno: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.suite = suite
        self.spec = spec
        self.loop = asyncio.get_event_loop()
        self.lineno = lineno

    def runtest(self) -> None:
        """
        Run the test.
        """

        yaml_file = self.parent
        while yaml_file and not isinstance(yaml_file, YamlFile):
            yaml_file = yaml_file.parent

        if not yaml_file:
            raise RuntimeError("Test can be run only within a YamlFile context.")

        self.loop.run_until_complete(
            self.suite.run_test(self.spec, cast(YamlFile, yaml_file).rest_exit_stack, cast(YamlFile, yaml_file).rest_context)
        )

    def repr_failure(
        self,
        excinfo: ExceptionInfo[BaseException],
        style: TracebackStyle | None = None,
    ) -> str | TerminalRepr:
        """
        Return a string representation of the failure.
        """

        if isinstance(excinfo.value, RestAssertionError):
            return str(excinfo.value)

        if isinstance(excinfo.value, TestMalformed):
            return str(excinfo.value)

        return super().repr_failure(excinfo)

    def reportinfo(self) -> tuple[os.PathLike[str] | str, int | None, str]:
        """
        Report information about the test case.
        """

        return (
            self.parent.path,
            self.lineno + 1 if self.lineno else None,
            self.spec.safe_name,
        )


def pytest_collect_file(parent: pytest.Item, file_path: PosixPath) -> YamlFile | None:
    """Collect pytest files."""
    if file_path.suffix == ".yaml" and file_path.name.startswith("test_"):
        return YamlFile.from_parent(parent, path=file_path)
    return None
