import asyncio
from collections.abc import Collection
from glob import glob

from pytest_resttest.models import Suite
from pytest_resttest.reporter.console import ConsoleReporter


class TestRunner:
    """
    Runner for the REST tests, if used stand-alone outside of pytest framework.
    """

    def __init__(self) -> None:
        self.reporter = ConsoleReporter()

    async def run_tests(self, suites: Collection[Suite]) -> None:
        """
        Run the discovered test suites.
        """

        self.reporter.report_start()

        for suite in suites:
            await suite(self.reporter)

        self.reporter.report_end()

    @staticmethod
    def scan_tests() -> Collection[Suite]:
        """
        Scan for test suites in the current directory and return them.
        This is a placeholder implementation; actual scanning logic should be implemented.
        """

        out: list[Suite] = []

        for file in sorted(glob("**/test_*.yaml", recursive=True)):
            out.append(Suite.load_suite_from_file(file))

        return out

    def __call__(self) -> None:
        """
        Run the pytest-resttest.
        """

        suites = self.scan_tests()

        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.run_tests(suites))
