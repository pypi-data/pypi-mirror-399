from collections.abc import Iterable
from itertools import chain, islice
from types import GeneratorType
from typing import Any

from jinja2 import StrictUndefined
from jinja2.nativetypes import NativeCodeGenerator, NativeEnvironment, NativeTemplate


def native_concat(values: Iterable[Any]) -> Any | None:
    """
    Return a native Python type from the list of compiled nodes. If
    the result is a single node, its value is returned. Otherwise, the
    nodes are concatenated as strings.

    The difference from the default Jinja2 nativetypes concat is that there is no parsing of string returned from the template
    to provide backward compatibility with pre-jinja2 tests. Non-jinja2 strings are returned as strings.

    :param values: Iterable of outputs to concatenate.
    """
    head = list(islice(values, 2))

    if not head:
        return None

    if len(head) == 1:
        raw = head[0]
        if not isinstance(raw, str):
            return raw
    else:
        if isinstance(values, GeneratorType):
            values = chain(head, values)
        raw = "".join([str(v) for v in values])

    return raw


class CodeGenerator(NativeCodeGenerator):
    """Native code generator for Jinja2, that does not do stringification of the output."""

    def _output_const_repr(self, group: Iterable[Any]) -> str:
        return repr(self.environment.concat(group))


class Environment(NativeEnvironment):
    """Native environment for Jinja2, which uses the custom CodeGenerator and concat method."""

    concat = staticmethod(native_concat)
    code_generator_class = CodeGenerator


class Template(NativeTemplate):
    """Native template for Jinja2, which uses the custom Environment."""

    environment_class = Environment


# Because of cyclic dependency, we need to set the template class in the environment after it has been defined.
Environment.template_class = Template  # type: ignore[attr-defined]  # it is there...


# Jinja2 environment for the resttest.
JINJA_ENV = Environment(undefined=StrictUndefined, enable_async=True)
