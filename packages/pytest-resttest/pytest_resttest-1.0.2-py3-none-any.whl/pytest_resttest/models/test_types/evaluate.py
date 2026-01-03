from contextlib import AsyncExitStack
from typing import Any

from pytest_resttest.compare.complex_compare import complex_compare_v2
from pytest_resttest.jinja import evaluate_jinja, evaluate_jinja_recursive
from pytest_resttest.models.exceptions import JinjaEvaluateError, RestAssertionError, TestMalformed
from pytest_resttest.models.suite import Suite
from pytest_resttest.models.test_types.base import BaseTest


class EvaluateTest(BaseTest):
    """
    Evaluate a template and optionally compare it with result.
    """

    template: str
    result: Any = None

    async def __call__(self, suite: Suite, exit_stack: AsyncExitStack, context: dict[str, Any]) -> None:
        """
        Evaluate the template with optional result comparison.

        Args:
            suite (Suite): The test suite instance.
            exit_stack (AsyncExitStack): The async exit stack for cleanup.
            context (dict[str, Any]): Context dictionary for passing data between tests.
        """

        try:
            evaluated_result = await evaluate_jinja(self.template, context)
        except Exception as exc:
            raise TestMalformed([JinjaEvaluateError(loc=["template"], msg=str(exc), input=self.template)]) from exc

        if "result" in self.model_fields_set:
            try:
                if isinstance(self.result, (str, dict, list)):
                    expected_result = await evaluate_jinja_recursive(self.result, context)
                else:
                    expected_result = self.result
            except Exception as exc:
                raise TestMalformed([JinjaEvaluateError(loc=["result"], msg=str(exc), input=self.result)]) from exc

            errors = await complex_compare_v2(expected_result, evaluated_result, partial_content=False, context={**context})
            if errors:
                raise RestAssertionError("\n".join(["Test failed:", *errors]))


Suite.register_test_type(EvaluateTest)
