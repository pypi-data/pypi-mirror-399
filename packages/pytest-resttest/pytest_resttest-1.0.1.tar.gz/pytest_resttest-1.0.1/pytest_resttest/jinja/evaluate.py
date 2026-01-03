from collections.abc import Mapping
from typing import Any

from jinja2 import Undefined

from .env import JINJA_ENV


def is_template_string(maybe_template: str) -> bool:
    """Check if the input is a Jinja2 template."""
    return "{" in maybe_template and ("{%" in maybe_template or "{{" in maybe_template or "{#" in maybe_template)


async def evaluate_jinja(template: str, context: Mapping[str, Any] | None = None) -> Any:
    """
    Evaluate value via jinja2, with optional context.
    """

    if not is_template_string(template):
        return template

    if context is None:
        context = {}

    rendered = await JINJA_ENV.from_string(template).render_async(**context)

    if isinstance(rendered, Undefined):
        # pylint: disable=protected-access
        rendered._fail_with_undefined_error()

    return rendered


async def evaluate_jinja_recursive(
    template: str | dict[str, Any] | list[Any] | Any, context: dict[str, Any] | None = None, loc: list[str | int] | None = None
) -> Any:
    """
    Recursively evaluate Jinja templates in a string, dict, or list.
    """

    # pylint: disable=import-outside-toplevel
    from ..models.exceptions import JinjaEvaluateError, TestConfigError, TestMalformed

    if not loc:
        loc = []

    if isinstance(template, str):
        try:
            return await evaluate_jinja(template, context)
        except Exception as exc:
            raise TestMalformed([JinjaEvaluateError(loc=loc, msg=str(exc), input=template)]) from exc

    errors: list[TestConfigError] = []

    if isinstance(template, dict):
        out_dict: dict[str, Any] = {}

        for k, v in template.items():
            try:
                out_dict[k] = await evaluate_jinja_recursive(v, context, [*loc, k])
            except TestMalformed as exc:
                errors.extend(exc.errors)

        if errors:
            raise TestMalformed(errors)

        return out_dict

    if isinstance(template, list):
        out_list: list[Any] = []

        for idx, item in enumerate(template):
            try:
                out_list.append(await evaluate_jinja_recursive(item, context, [*loc, idx]))
            except TestMalformed as exc:
                errors.extend(exc.errors)

        if errors:
            raise TestMalformed(errors)

        return out_list

    return template
