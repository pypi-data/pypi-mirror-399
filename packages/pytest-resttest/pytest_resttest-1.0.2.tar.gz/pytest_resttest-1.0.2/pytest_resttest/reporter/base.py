from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytest_resttest.models.suite import Suite
    from pytest_resttest.models.test_types.base import BaseTest


class ReporterInterface(ABC):
    """
    Interface for reporting test execution events.
    """

    @abstractmethod
    def report_start(self) -> None:
        """Start of the test execution process."""

    @abstractmethod
    def report_end(self) -> None:
        """End of the test execution process."""

    @abstractmethod
    def report_suite_start(self, suite: Suite) -> None:
        """Start of a test suite execution."""

    @abstractmethod
    def report_suite_end(self, suite: Suite) -> None:
        """End of a test suite execution."""

    @abstractmethod
    def report_test_start(self, suite: Suite, test: BaseTest) -> None:
        """Start of a test execution within a suite."""

    @abstractmethod
    def report_test_skip(self, suite: Suite, test: BaseTest) -> None:
        """Report a skipped test within a suite."""

    @abstractmethod
    def report_test_fail(self, suite: Suite, test: BaseTest, exc: Exception) -> None:
        """Report a failed test within a suite, including the exception raised."""

    @abstractmethod
    def report_test_pass(self, suite: Suite, test: BaseTest) -> None:
        """Report a passed test within a suite."""

    @abstractmethod
    def report_test_end(self, suite: Suite, test: BaseTest) -> None:
        """End of a test execution within a suite."""
