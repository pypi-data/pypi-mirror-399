from __future__ import annotations

import curses
import sys
from typing import TYPE_CHECKING, ClassVar

from termcolor import colored

from pytest_resttest.reporter.base import ReporterInterface

if TYPE_CHECKING:
    from pytest_resttest.models.suite import Suite
    from pytest_resttest.models.test_types.base import BaseTest


class ConsoleReporter(ReporterInterface):
    # pylint: disable=too-many-instance-attributes

    """
    Test reporter that outputs results to the console.
    """

    COLOR_INFO: ClassVar[str] = "blue"
    COLOR_ERROR: ClassVar[str] = "red"
    COLOR_DEBUG: ClassVar[str] = "gray"
    COLOR_SUCCESS: ClassVar[str] = "green"
    COLOR_SKIP: ClassVar[str] = "yellow"

    def __init__(self) -> None:
        self.output = sys.stderr
        self.count_tests = 0
        self.count_passed = 0
        self.count_failed = 0
        self.count_skipped = 0

        self.suite_tests = 0
        self.suite_passed = 0
        self.suite_failed = 0
        self.suite_skipped = 0

        self.window = curses.initscr()
        self.width = self.window.getmaxyx()[1]

    def _centered_text(self, text: str, divider: str = "-") -> str:
        """
        Center the text within the console width, using a divider character.
        """
        text_len = len(text) + 2

        if text_len >= self.width:
            return text

        if not text:
            return divider * self.width

        padding = (self.width - text_len) // 2
        remainder = (self.width - text_len) % 2
        return f"{divider * padding} {text} {divider * (padding + remainder)}"

    def _write(self, text: str) -> None:
        """
        Write text to the console output.
        """
        print(text, file=self.output)

    def report_start(self) -> None:
        self._write(colored("Starting tests...", self.COLOR_INFO))

    def report_end(self) -> None:
        if self.count_failed == 0:
            self._write(colored(self._centered_text("Tests SUCCEEDED", "="), self.COLOR_SUCCESS))
        else:
            self._write(colored(self._centered_text("Tests FAILED", "="), self.COLOR_ERROR))

        self._write(f"Tests ran: {self.count_tests}")
        self._write(f"Passed: {self.count_passed}")
        self._write(f"Failed: {self.count_failed}")
        self._write(f"Skipped: {self.count_skipped}")

        self._write(colored(self._centered_text("", "="), self.COLOR_DEBUG))

    def report_suite_start(self, suite: Suite) -> None:
        self._write(
            colored(
                self._centered_text(f"Running test suite: {suite.name}"),
                self.COLOR_INFO,
            )
        )

        self.suite_tests = 0
        self.suite_passed = 0
        self.suite_failed = 0
        self.suite_skipped = 0

    def report_suite_end(self, suite: Suite) -> None:
        if self.suite_failed == 0:
            self._write(
                colored(
                    self._centered_text(f"Test suite {suite.name} SUCCEEDED"),
                    self.COLOR_SUCCESS,
                )
            )
        else:
            self._write(
                colored(
                    self._centered_text(f"Test suite {suite.name} FAILED"),
                    self.COLOR_ERROR,
                )
            )

        self._write(
            colored(
                f"Tests ran: {self.suite_tests}, "
                f"succeeded: {self.suite_passed}, "
                f"failed: {self.suite_failed}, "
                f"skipped: {self.suite_skipped}",
                self.COLOR_INFO,
            )
        )

    def report_test_start(self, suite: Suite, test: BaseTest) -> None:
        pass

    def report_test_skip(self, suite: Suite, test: BaseTest) -> None:
        self._write(colored(f"  - {test.name} - SKIPPED", self.COLOR_SKIP))

    def report_test_fail(self, suite: Suite, test: BaseTest, exc: Exception) -> None:
        self._write(colored(f"  - {test.name} - FAILED", self.COLOR_ERROR))
        self._write(colored(f"    Error: {exc}", self.COLOR_DEBUG))

    def report_test_pass(self, suite: Suite, test: BaseTest) -> None:
        self._write(colored(f"  - {test.name} - PASSED", self.COLOR_SUCCESS))

    def report_test_end(self, suite: Suite, test: BaseTest) -> None:
        pass
