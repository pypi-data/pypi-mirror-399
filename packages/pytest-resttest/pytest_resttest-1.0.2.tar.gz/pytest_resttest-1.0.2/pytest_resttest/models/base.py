import pydantic
from pydantic import ConfigDict


class BaseModel(pydantic.BaseModel):
    """
    Base class for resttest models.

    The extra="forbid" is mandatory for YAML to Suite loading works regarding various test and fixture types.
    """

    model_config = ConfigDict(
        extra="forbid",
    )
