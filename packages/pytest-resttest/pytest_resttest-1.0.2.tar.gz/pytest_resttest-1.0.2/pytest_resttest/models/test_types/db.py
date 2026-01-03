import importlib
from abc import ABC
from contextlib import AsyncExitStack
from datetime import UTC, tzinfo
from math import isnan
from typing import Any, ClassVar, Literal, Self
from zoneinfo import ZoneInfo

from asyncdb import BoolResult, TransactionContext
from asyncdb.aiomysql import Result, Transaction, TransactionFactory
from pydantic import Field, GetCoreSchemaHandler, model_validator
from pydantic_core import CoreSchema, core_schema

from pytest_resttest.compare.complex_compare import complex_compare
from pytest_resttest.jinja.evaluate import evaluate_jinja
from pytest_resttest.models.base import BaseModel
from pytest_resttest.models.exceptions import RestAssertionError
from pytest_resttest.models.jinja import Jinja
from pytest_resttest.models.suite import Suite
from pytest_resttest.models.test_types.base import BaseTest


class ImportDatabaseTarget(BaseModel):
    """
    Target specifier for importing a database connection factory.
    """

    import_name: str = Field(alias="import")


class tzinfo_pydantic(tzinfo, ABC):  # noqa: N801
    # pylint: disable=invalid-name
    """
    Pydantic type hints for parsing tzinfo objects.
    """

    @classmethod
    def _from_str(cls, value: str | tzinfo) -> tzinfo:
        if isinstance(value, str):
            return ZoneInfo(value)

        if isinstance(value, tzinfo):
            return value

        raise ValueError("Unexpected value for tzinfo: must be a string or tzinfo instance.")

    @classmethod
    def _serialize(cls, value: tzinfo) -> str:
        if isinstance(value, ZoneInfo):
            return value.key

        if value.utcoffset(None) is None or isnan(value.utcoffset(None).total_seconds()):
            return "UTC"

        return value.tzname(None) or "UTC"

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        # pylint: disable=unused-argument
        return core_schema.no_info_before_validator_function(
            cls._from_str,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._serialize, return_schema=core_schema.str_schema()
            ),
        )


class MySQLConfig(BaseModel):
    """
    Target specifier for MySQL database connections.
    """

    host: str = "localhost"
    port: int = 3306
    user: str = "root"
    password: str = ""
    database: str = ""
    charset: str = "utf8mb4"
    max_pool_size: int = 100
    max_spare_conns: int = 10
    min_spare_conns: int = 5
    max_conn_lifetime: int | None = None
    max_conn_usage: int | None = None
    connect_timeout: int | None = None
    read_timeout: int | None = None
    write_timeout: int | None = None
    wait_timeout: int | None = None
    remote_app: str | None = None
    timezone: tzinfo_pydantic = Field(default=UTC)  # type: ignore[assignment]


type DatabaseTarget = ImportDatabaseTarget | MySQLConfig


class Query(BaseModel):
    """
    Query model for database operations.
    """

    query: Jinja[str]
    args: list[Jinja[Any]] = Field(default_factory=list)


class DatabaseQuery(BaseTest):
    """
    Test type for executing database queries.
    """

    __pool_cache__: ClassVar[dict[Any, TransactionFactory]] = {}

    target: DatabaseTarget
    queries: list[Jinja[str] | Query]
    responses: list[Jinja[list[Jinja[list[Any] | dict[str, Any]]] | Literal[True]]] | None = Field(default=None)

    partial: bool = True

    @model_validator(mode="after")
    def validate_queries(self) -> Self:
        """
        Ensure that the number of queries matches the number of responses if responses are provided.
        """

        if self.responses and len(self.queries) != len(self.responses):
            raise ValueError("The number of queries must match the number of responses.")

        return self

    def transaction(self, exit_stack: AsyncExitStack) -> TransactionContext[Transaction]:
        """
        Create a transaction context for the database connection.
        """

        if isinstance(self.target, MySQLConfig):
            key: Any = (
                self.target.host,
                self.target.port,
                self.target.user,
                self.target.password,
                self.target.database,
            )
            if key not in self.__class__.__pool_cache__:
                self.__class__.__pool_cache__[key] = TransactionFactory(self.target)  # type: ignore[arg-type]
                exit_stack.push_async_callback(self.__class__.__pool_cache__[key].pool.close)
        else:
            key = self.target.import_name
            if key not in self.__class__.__pool_cache__:
                module, symbol = key.rsplit(":", 1)
                imported_module = importlib.import_module(module)

                self.__class__.__pool_cache__[key] = getattr(imported_module, symbol)
                exit_stack.push_async_callback(self.__class__.__pool_cache__[key].pool.close)

        self.__class__.__pool_cache__[key].ensure_pool()
        return self.__class__.__pool_cache__[key].transaction()

    async def _process_response(self, query_idx: int, res: Result, context: dict[str, Any]) -> list[str]:
        if self.responses is None:
            return []

        errors: list[str] = []

        expected_response = self.responses[query_idx]  # pylint: disable=unsubscriptable-object

        if isinstance(expected_response, str):
            expected_response = await evaluate_jinja(expected_response, context)

        if isinstance(res, BoolResult) and isinstance(expected_response, bool):
            if bool(res) != expected_response:
                errors.append(f"Query {query_idx} expected boolean result {expected_response}, got {bool(res)}.")

            return errors

        if not isinstance(expected_response, list):
            raise TypeError(
                f"Expected response {query_idx} is not a list of rows. Expected a list, got {type(expected_response)}."
            )

        for row_idx, expected_row in enumerate(expected_response):
            if isinstance(expected_row, str):
                expected_row = await evaluate_jinja(expected_row, context)

            if not isinstance(expected_row, (list, dict)):
                raise TypeError(f"Expected row {row_idx} to be a list or dict, but got {type(expected_row)}")

            if isinstance(expected_row, list):
                row: list[Any] | dict[str, Any] = await res.fetch_list()
            else:
                row = await res.fetch_dict()

            errors.extend(
                await complex_compare(
                    expected_row,
                    row,
                    self.partial,
                    context,
                    f"Query {query_idx}, row {row_idx}",
                )
            )

        return errors

    async def __call__(self, suite: Suite, exit_stack: AsyncExitStack, context: dict[str, Any]) -> None:
        """
        Execute the database queries and compare the results with expected responses.
        """

        errors: list[str] = []

        async with self.transaction(exit_stack) as trx:
            for query_idx, query in enumerate(self.queries):
                if isinstance(query, str):
                    query = Query(query=query)

                res = await trx.query(
                    await evaluate_jinja(query.query, context),
                    *[await evaluate_jinja(arg, context) if isinstance(arg, str) else arg for arg in query.args],
                )

                errors.extend(await self._process_response(query_idx, res, context))

                await res.close()
            await trx.commit()

        if errors:
            raise RestAssertionError("\n".join(errors))


Suite.register_test_type(DatabaseQuery)
