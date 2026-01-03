import importlib
import os
from collections.abc import Collection, Mapping
from contextlib import AsyncExitStack
from io import BytesIO
from typing import IO, Any, ClassVar, Self, cast
from urllib.parse import parse_qs, urlparse, urlunparse

import orjson
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncBaseTransport, AsyncClient, AsyncHTTPTransport, Response
from pydantic import Field, model_validator
from termcolor import colored

from pytest_resttest.compare.complex_compare import complex_compare_v2
from pytest_resttest.compare.partial import PartialList, Unsorted
from pytest_resttest.compare.repr import boxed
from pytest_resttest.jinja.evaluate import evaluate_jinja, evaluate_jinja_recursive
from pytest_resttest.lib.format_struct import format_struct
from pytest_resttest.models.base import BaseModel
from pytest_resttest.models.exceptions import JinjaEvaluateError, RestAssertionError, TestConfigError, TestMalformed
from pytest_resttest.models.http_types import ASGITarget, Cookies, Headers, HttpTarget, Loc, Query, ScalarType
from pytest_resttest.models.jinja import Jinja
from pytest_resttest.models.suite import Suite
from pytest_resttest.models.test_types.base import BaseTest


class HttpTestBase(BaseTest):
    """Represents a test, that is executed over HTTP."""

    target: HttpTarget | None = None
    endpoint: str
    method: str
    headers: Headers | None = None
    cookies: Cookies | None = None
    query: Query | None = None

    status: int | str | None = None
    response: Any | None = None
    response_headers: Headers | None = None
    response_cookies: Cookies | None = None
    partial: bool = True

    _client_pool: ClassVar[dict[str, AsyncClient]] = {}

    @staticmethod
    async def _process_dict(
        in_dict: Mapping[str, ScalarType | Collection[ScalarType]],
        context: Mapping[str, Any],
        errors: list[TestConfigError],
        loc: Loc,
        evaluate_templates: bool = True,
        normalize_keys: bool = True,
    ) -> dict[str, str | list[str]]:
        out: dict[str, str | list[str] | None] = {}

        for key, value in in_dict.items():
            if normalize_keys:
                normalized_key = key.lower()
            else:
                normalized_key = key

            if isinstance(value, str):
                try:
                    out[normalized_key] = (
                        await evaluate_jinja(value, context) if evaluate_templates and isinstance(value, str) else str(value)
                    )
                except Exception as exc:  # pylint: disable=broad-except
                    errors.append(
                        JinjaEvaluateError(
                            loc=[*loc, key],
                            msg=str(exc),
                            input=value,
                        )
                    )
            elif isinstance(value, list):
                out_list: list[str] = []

                for idx, item in enumerate(value):
                    try:
                        out_list.append(
                            await evaluate_jinja(item, context) if evaluate_templates and isinstance(item, str) else str(item)
                        )
                    except Exception as exc:  # pylint: disable=broad-except
                        errors.append(JinjaEvaluateError(loc=[*loc, key, idx], msg=str(exc), input=item))

                out[normalized_key] = out_list

            elif value is None:
                out[normalized_key] = value

            else:
                out[normalized_key] = str(value)

        return out

    @staticmethod
    async def _process_list(
        in_list: Collection[tuple[str, ScalarType]],
        context: Mapping[str, Any],
        errors: list[TestConfigError],
        loc: Loc,
        evaluate_templates: bool = True,
    ) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []

        for idx, item in enumerate(in_list):
            name, value = item
            try:
                out.append(
                    (
                        name.lower(),
                        await evaluate_jinja(value, context) if evaluate_templates and isinstance(value, str) else str(value),
                    )
                )
            except Exception as exc:  # pylint: disable=broad-except
                errors.append(JinjaEvaluateError(loc=[*loc, idx, 1], msg=str(exc), input=value))

        return out

    async def _process_complex(
        self,
        in_object_list: Collection[tuple[Loc, Headers | Cookies | Query]],
        context: Mapping[str, Any],
        evaluate_templates: bool = True,
        normalize_keys: bool = True,
    ) -> list[tuple[str, str]]:
        # pylint: disable=too-many-branches

        out_list: list[tuple[str, str]] = []
        out_dict: dict[str, str | list[str]] = {}

        errors: list[TestConfigError] = []

        for loc, in_object in in_object_list:
            if isinstance(in_object, str):
                try:
                    in_object = await evaluate_jinja(in_object, context) if evaluate_templates else in_object
                except Exception as exc:  # pylint: disable=broad-except
                    errors.append(
                        JinjaEvaluateError(
                            loc=loc,
                            msg=str(exc),
                            input=in_object,
                        )
                    )

            if isinstance(in_object, Mapping):
                # Merge mapping, overwriting duplicate entries.
                processed_in_object = await self._process_dict(
                    in_object, context, errors, loc, evaluate_templates, normalize_keys
                )
                for key, val in processed_in_object.items():
                    if val is not None:
                        out_dict[key] = val
                    else:
                        out_dict.pop(key, None)

            elif isinstance(in_object, Collection):
                # Append to list, not overwrite duplicate entries.
                out_list.extend(
                    await self._process_list(
                        cast(Collection[tuple[str, ScalarType]], in_object),
                        context,
                        errors,
                        loc,
                        evaluate_templates,
                    )
                )

            else:
                errors.append(TestConfigError(loc=loc, type="type_error", msg="Must be mapping or list.", input=in_object))

        if errors:
            raise TestMalformed(errors)

        for key, val in out_dict.items():
            if isinstance(val, list):
                for item in val:
                    out_list.append((key, item))

            else:
                out_list.append((key, val))

        return out_list

    async def _process_headers(
        self,
        headers: Collection[tuple[Loc, Headers]],
        context: Mapping[str, Any],
        evaluate_templates: bool = True,
    ) -> list[tuple[str, str]]:
        return await self._process_complex(headers, context, evaluate_templates=evaluate_templates)

    async def _process_query(
        self,
        query: Collection[tuple[Loc, Query]],
        context: Mapping[str, Any],
        evaluate_templates: bool = True,
    ) -> list[tuple[str, str]]:
        return await self._process_complex(query, context, evaluate_templates=evaluate_templates, normalize_keys=False)

    async def _process_cookies(
        self,
        cookies: Collection[tuple[Loc, Cookies]],
        context: dict[str, Any],
        evaluate_templates: bool = True,
    ) -> list[tuple[str, str]]:
        return await self._process_complex(cookies, context, evaluate_templates=evaluate_templates)

    async def build_request_args(self, suite: Suite, exit_stack: AsyncExitStack, context: dict[str, Any]) -> dict[str, Any]:
        """
        Build the HTTP request arguments from the test configuration. Note that this method does not fill request body,
        as there are subclasses for that.
        """
        # pylint: disable=unused-argument

        params: dict[str, Any] = {}

        errors: list[TestConfigError] = []

        try:
            params["method"] = await evaluate_jinja(self.method, context) if isinstance(self.method, str) else str(self.method)
        except Exception as exc:  # pylint: disable=broad-except
            errors.append(JinjaEvaluateError(loc=["method"], msg=str(exc), input=self.method))

        url_query: dict[str, list[str]] = {}

        try:
            url = urlparse(await evaluate_jinja(self.endpoint, context) if isinstance(self.endpoint, str) else str(self.endpoint))
            url_query = parse_qs(url.query, keep_blank_values=True, strict_parsing=True) if url.query else {}

            params["url"] = urlunparse((url.scheme, url.netloc, url.path, url.params, "", url.fragment))
        except Exception as exc:  # pylint: disable=broad-except
            errors.append(JinjaEvaluateError(loc=["endpoint"], msg=str(exc), input=self.endpoint))

        try:
            params["params"] = await self._process_query(
                [
                    (["endpoint", "query"], url_query),  # type: ignore[list-item]
                    (["query"], self.query if self.query else []),
                ],
                context,
            )

            if not params["params"]:
                params.pop("params", None)

        except TestMalformed as exc:
            errors.extend(exc.errors)

        try:
            params["headers"] = await self._process_headers(
                [
                    (["defaults", "headers"], suite.defaults.headers if suite.defaults.headers else []),
                    (["headers"], self.headers if self.headers else []),
                ],
                context,
            )

            if not params["headers"]:
                params.pop("headers", None)

        except TestMalformed as exc:
            errors.extend(exc.errors)

        try:
            params["cookies"] = await self._process_cookies(
                [
                    (["defaults", "cookies"], suite.defaults.cookies if suite.defaults.cookies else []),
                    (["cookies"], self.cookies if self.cookies else []),
                ],
                context,
            )

            if not params["cookies"]:
                params.pop("cookies", None)

        except TestMalformed as exc:
            errors.extend(exc.errors)

        if errors:
            raise TestMalformed(errors)

        return params

    async def client(self, target: HttpTarget, stack: AsyncExitStack, context: dict[str, Any]) -> AsyncClient:
        # pylint: disable=protected-access  # it's my class, wtf?

        """
        Get an HTTP client for the given target.
        """

        if isinstance(target, str):
            transport: AsyncBaseTransport = AsyncHTTPTransport()

            target = await evaluate_jinja(target, context)

            base_url: str = str(target)
            cache_key: str = str(target)

        elif isinstance(target, ASGITarget):
            module, symbol = target.app.rsplit(":", 1)
            imported_module = importlib.import_module(module)
            app = getattr(imported_module, symbol)
            cache_key = target.app

            transport = ASGITransport(app=app, raise_app_exceptions=False)
            base_url = "http://resttest"

            if self.__class__._client_pool.get(cache_key) is None:
                await stack.enter_async_context(LifespanManager(app))

        else:
            raise TestMalformed(
                [TestConfigError(loc=["target"], type="type_error", msg=f"Unsupported target type: {type(target)}", input=target)]
            )

        if self.__class__._client_pool.get(cache_key) is None:

            def del_client_on_exit() -> None:
                self.__class__._client_pool.pop(cache_key, None)

            self.__class__._client_pool[cache_key] = await stack.enter_async_context(
                AsyncClient(
                    transport=transport,
                    base_url=base_url,
                )
            )
            stack.callback(del_client_on_exit)

        return self.__class__._client_pool.get(cache_key)

    async def evaluate_http_status(self, response: Response, context: dict[str, Any], errors: list[str]) -> bool:
        """
        Evaluate the HTTP response status code against the expected value defined in the test.
        """

        status_errors = await complex_compare_v2(
            self.status,
            response.status_code,
            False,
            {
                **context,
                "response": response,
            },
        )

        if status_errors:
            if errors:
                errors.append("")

            errors.append(
                boxed(str(status_errors), header="Response status code does not match expected:", color="red", attrs=["bold"])
            )

            return False

        return True

    async def evaluate_response_data(
        self, response: Response, context: dict[str, Any], errors: list[str], tail: list[str]
    ) -> bool:
        """
        Evaluate the HTTP response body against the expected values defined in the test.
        """

        response_data: Any = response.content

        if response.headers.get("content-type", "").startswith("text/"):
            response_data = response.text

        if response.headers.get("content-type", "").startswith("application/json"):
            response_data = orjson.loads(response_data)

        response_context = {
            **context,
            "response": response,
            "values": response_data,
        }

        body_errors = await complex_compare_v2(
            self.response,
            response_data,
            self.partial,
            response_context,
        )

        if body_errors:
            if errors:
                errors.append("")

            errors.append(
                boxed(
                    str(body_errors),
                    header="Response body does not match expected:",
                    color="red",
                    attrs=["bold"],
                )
            )

            tail.extend(
                [
                    boxed(
                        "\n".join(format_struct(self.response)),
                        header=f"{colored('\u25a0', 'red', force_color=True)} Expected response (status={self.status}):"
                        if self.status
                        else "Expected response:",
                        color="white",
                    ),
                    "",
                    boxed(
                        "\n".join(format_struct(response_data)),
                        header=f"{colored('\u25a0', 'green', force_color=True)} Actual response (status={response.status_code})",
                        color="white",
                    ),
                    "",
                ]
            )

            return False

        return True

    async def evaluate_headers(self, resp: Response, context: dict[str, Any], errors: list[str], tail: list[str]) -> bool:
        """Compare response headers with expected headers."""

        response_headers = await self._process_headers(
            [(["actual", "headers"], dict(resp.headers))],
            context,
            evaluate_templates=False,
        )

        headers_context = {
            **context,
            "response": resp,
            "headers": response_headers,
        }

        expected_headers = await self._process_headers(
            [(["response", "headers"], self.response_headers)],
            context,
            evaluate_templates=False,
        )

        header_errors = await complex_compare_v2(
            PartialList(expected_headers),
            response_headers,
            True,
            headers_context,
        )

        if header_errors:
            if errors:
                errors.append("")

            errors.append(
                boxed(
                    str(header_errors),
                    header="Response headers do not match expected:",
                    color="red",
                    attrs=["bold"],
                )
            )

            tail.extend(
                [
                    boxed(
                        "\n".join(format_struct(expected_headers)),
                        header=f"{colored('\u25a0', 'red', force_color=True)} Expected headers:",
                        color="white",
                    ),
                    "",
                    boxed(
                        "\n".join(format_struct(response_headers)),
                        header=f"{colored('\u25a0', 'green', force_color=True)} Actual headers:",
                        color="white",
                    ),
                    "",
                ]
            )

            return False

        return True

    async def evaluate_cookies(self, resp: Response, context: dict[str, Any], errors: list[str], tail: list[str]) -> bool:
        """Compare response cookies with expected cookies."""

        response_cookies = await self._process_cookies(
            [(["response", "cookies"], dict(resp.cookies.items()))],
            context,
            evaluate_templates=False,
        )

        cookies_context = {
            **context,
            "response": resp,
            "cookies": response_cookies,
        }

        expected_cookies = await self._process_cookies(
            [(["actual", "cookies"], self.response_cookies)], context, evaluate_templates=False
        )

        cookie_errors = await complex_compare_v2(
            PartialList(expected_cookies) if self.partial else Unsorted(expected_cookies),
            response_cookies,
            True,
            cookies_context,
        )

        if cookie_errors:
            if errors:
                errors.append("")

            errors.append(
                boxed(
                    str(cookie_errors),
                    header="Response cookies do not match expected:",
                    color="red",
                    attrs=["bold"],
                )
            )

            tail.extend(
                [
                    boxed(
                        header=f"{colored('\u25a0', 'red', force_color=True)} Expected cookies:",
                        text="\n".join(format_struct(expected_cookies)),
                        color="white",
                    ),
                    "",
                    boxed(
                        header=f"{colored('\u25a0', 'green', force_color=True)} Actual cookies:",
                        text="\n".join(format_struct(response_cookies)),
                        color="white",
                    ),
                    "",
                ]
            )

            return False

        return True

    async def evaluate_http_response(self, resp: Response, context: dict[str, Any]) -> None:
        """
        Evaluate the HTTP response against the expected values defined in the test.
        """

        errors: list[str] = []
        tail: list[str] = []

        success: bool = True

        if self.status is not None:
            success &= await self.evaluate_http_status(resp, context, errors)

        if "response" in self.model_fields_set:
            success &= await self.evaluate_response_data(resp, context, errors, tail)
        elif not success:
            # If we don't check the body, but something else failed, show the body for context
            tail.extend(
                [
                    boxed(
                        "\n".join(format_struct(resp.content)),
                        header=f"{colored('\u25a0', 'green', force_color=True)} Actual response (status={resp.status_code})",
                        color="white",
                    ),
                    "",
                ]
            )

        if self.response_headers:
            success &= await self.evaluate_headers(resp, context, errors, tail)

        if self.response_cookies:
            success &= await self.evaluate_cookies(resp, context, errors, tail)

        if errors and tail:
            errors.append("")
            errors.extend(tail)

        if not success:
            errors.extend(
                [
                    boxed(
                        "\n".join(format_struct(context["request"])),
                        "Request:",
                        color="white",
                    ),
                    "",
                ]
            )

            raise RestAssertionError("\n".join(["Test failed:", *errors]))

    async def __call__(self, suite: Suite, exit_stack: AsyncExitStack, context: dict[str, Any]) -> None:
        """
        Execute the HTTP test.
        """

        session = await self.client(self.target if self.target else suite.defaults.target, exit_stack, context)
        request_args = await self.build_request_args(suite, exit_stack, context)

        resp = await session.request(**request_args)
        try:
            await self.evaluate_http_response(
                resp,
                {
                    **context,
                    "request": request_args,
                },
            )
        finally:
            session.cookies.clear()  # Clear cookies after the request to avoid side effects in other tests


class UploadRawPath(BaseModel):
    """
    Model specifying the request body should be loaded from file.
    """

    path: str

    _content: bytes

    @model_validator(mode="after")
    def _load_file_from_path(self) -> Self:
        real_path = os.path.realpath(self.path)
        with open(real_path, "rb") as f:
            self._content = f.read()

        return self

    @property
    def content(self) -> bytes:
        """
        Return content of the file specified by path.
        """

        return self._content


class HttpTestPlainBody(HttpTestBase):
    """Represents a test, that is executed over HTTP with a plain body."""

    body: str | bytes | None | UploadRawPath = None

    async def build_request_args(self, suite: Suite, exit_stack: AsyncExitStack, context: dict[str, Any]) -> dict[str, Any]:
        """
        Build the HTTP request arguments from the test configuration, including the body as plaintext.
        """

        errors: list[TestConfigError] = []

        try:
            params = await super().build_request_args(suite, exit_stack, context)
        except TestMalformed as exc:
            errors.extend(exc.errors)
            params = {}

        if "body" in self.model_fields_set:
            try:
                if isinstance(self.body, str):
                    params["content"] = await evaluate_jinja(self.body, context)

                elif isinstance(self.body, bytes):
                    params["content"] = self.body

                elif isinstance(self.body, UploadRawPath):
                    params["content"] = self.body.content
            except Exception as exc:  # pylint: disable=broad-exception-caught
                errors.append(
                    JinjaEvaluateError(
                        loc=["body"],
                        msg=str(exc),
                        input=self.body,
                    )
                )

        if errors:
            raise TestMalformed(errors)

        return params


class HttpTestJsonBody(HttpTestBase):
    """Represents a test, that is executed over HTTP with a JSON body."""

    # This needs to be named differently, as pydantic still contains a `json()` method on models as backward
    # compatible layer with Pydantic v1.
    json_data: dict[str, Any] | list[Any] | str | int | float = Field(alias="json")

    async def build_request_args(self, suite: Suite, exit_stack: AsyncExitStack, context: dict[str, Any]) -> dict[str, Any]:
        """
        Build the HTTP request arguments from the test configuration, including the body as JSON data.
        """

        errors: list[TestConfigError] = []

        try:
            params = await super().build_request_args(suite, exit_stack, context)
        except TestMalformed as exc:
            errors.extend(exc.errors)
            params = {}

        try:
            params.setdefault("headers", []).append(("Content-Type", "application/json"))
            params["data"] = orjson.dumps(
                await evaluate_jinja_recursive(self.json_data, context, ["json"])
                if isinstance(self.json_data, (str, dict, list))
                else self.json_data
            )
        except TestMalformed as exc:
            errors.extend(exc.errors)

        if errors:
            raise TestMalformed(errors)

        return params


class HttpTestFormBody(HttpTestBase):
    """Represents a test, that is executed over HTTP with a form body."""

    form: dict[str, Any]

    async def build_request_args(self, suite: Suite, exit_stack: AsyncExitStack, context: dict[str, Any]) -> dict[str, Any]:
        """
        Build the HTTP request arguments from the test configuration, including the body as form data.
        """

        errors: list[TestConfigError] = []

        try:
            params = await super().build_request_args(suite, exit_stack, context)
        except TestMalformed as exc:
            errors.extend(exc.errors)
            params = {}

        if self.form is not None:
            try:
                params["data"] = (
                    await evaluate_jinja_recursive(self.form, context, ["form"]) if isinstance(self.form, dict) else self.form
                )
            except TestMalformed as exc:
                errors.extend(exc.errors)

        if errors:
            raise TestMalformed(errors)

        return params


class UploadFile(BaseModel):
    """
    Model representing uploaded file, where file content is part of the test file.
    """

    filename: str | None = Field(default=None)
    content: Jinja[bytes]
    content_type: str | None = Field(default=None, alias="contentType")


class UploadPath(BaseModel):
    """
    Model representing uploaded file, where file content is loaded from disk.
    """

    filename: str | None = Field(default=None)
    path: str
    content_type: str | None = Field(default=None, alias="contentType")

    _content: bytes

    @model_validator(mode="after")
    def _load_file_content(self) -> Self:
        real_path = os.path.realpath(self.path)

        with open(real_path, "rb") as f:
            self._content = f.read()

        return self

    @property
    def content(self) -> bytes:
        """
        Return content of the file specified by path.
        """

        return self._content


class HttpTestFileUpload(HttpTestFormBody):
    """Represents a test, that is executed over HTTP with a file upload form body."""

    form: dict[str, Any] | None = Field(default=None)
    files: dict[str, UploadFile | UploadPath] | list[tuple[str, UploadFile | UploadPath]]

    async def build_request_args(self, suite: Suite, exit_stack: AsyncExitStack, context: dict[str, Any]) -> dict[str, Any]:
        """
        Build the HTTP request arguments from the test configuration, including the body as form data.
        """

        errors: list[TestConfigError] = []

        try:
            params = await super().build_request_args(suite, exit_stack, context)
        except TestMalformed as exc:
            errors.extend(exc.errors)
            params = {}

        try:
            files: list[tuple[str, tuple[str, IO[bytes], str | None]]] = []

            for field_name, file_info in self.files.items() if isinstance(self.files, dict) else self.files:
                if isinstance(file_info.content, str):
                    content: IO[bytes] = BytesIO(await evaluate_jinja(file_info.content, context))
                else:
                    content = BytesIO(file_info.content)

                exit_stack.callback(content.close)
                files.append((field_name, (file_info.filename, content, file_info.content_type)))

            params["files"] = files
        except TestMalformed as exc:
            errors.extend(exc.errors)

        if errors:
            raise TestMalformed(errors)

        return params


Suite.register_test_type(HttpTestPlainBody)
Suite.register_test_type(HttpTestJsonBody)
Suite.register_test_type(HttpTestFormBody)
Suite.register_test_type(HttpTestFileUpload)

__all__ = ["HttpTestBase", "HttpTestFormBody", "HttpTestJsonBody", "HttpTestPlainBody"]
