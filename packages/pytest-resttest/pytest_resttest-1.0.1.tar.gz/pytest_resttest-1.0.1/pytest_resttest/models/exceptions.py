from typing import Any

import pydantic


class RestAssertionError(AssertionError):
    """
    Exception raised when a REST request does not match expected values.
    """


class SuiteLoadError(Exception):
    """
    Exception raised when a test suite cannot be loaded.
    """


class TestConfigError(pydantic.BaseModel):
    """
    Model representing a single error in individual test.
    """

    loc: list[str | int]
    type: str
    msg: str
    ctx: dict[str, Any] = None
    input: Any = None


class JinjaEvaluateError(TestConfigError):
    """
    Model representing a single error caused by Jinja template evaluation.
    """

    type: str = "template_evaluate_error"


class TestMalformed(AssertionError):
    """
    Exception raised when a test is malformed.
    """

    def __init__(self, errors: list[TestConfigError]) -> None:
        self.errors = errors

    def __str__(self) -> str:
        if not self.errors:
            return "No errors found."

        out = ["Test configuration is invalid:"]

        for error in self.errors:
            out.append(".".join(map(str, error.loc)))

            args = error.model_dump(exclude_unset=True, exclude={"loc", "msg"})

            if not args:
                out.append(f"  {error.msg}")
            else:
                fmt_args = [f"{key}={value!r}" for key, value in args.items()]
                out.append(f"  {error.msg} [{', '.join(fmt_args)}]")

        return "\n".join(out)
