from pydantic import AnyHttpUrl

from pytest_resttest.models.base import BaseModel
from pytest_resttest.models.jinja import Jinja


class ASGITarget(BaseModel):
    """Model describing ASGI application as target for HTTP request tests."""

    app: str


type Loc = list[str | int]

type ScalarType = str | int | float | bool
type Headers = Jinja[dict[str, Jinja[ScalarType | None] | list[Jinja[ScalarType]]] | list[tuple[str, Jinja[ScalarType]]]]
type Cookies = Jinja[dict[str, Jinja[ScalarType | None] | list[Jinja[ScalarType]]] | list[tuple[str, Jinja[ScalarType]]]]
type Query = Jinja[dict[str, Jinja[ScalarType | None] | list[Jinja[ScalarType]]] | list[tuple[str, Jinja[ScalarType]]]]

type HttpTarget = AnyHttpUrl | ASGITarget | str
