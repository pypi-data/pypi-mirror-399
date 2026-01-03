from typing import Annotated
from pydantic import Field
from pydantic import BaseModel
from paddle.schemas import Meta, MetaPaginated


class Response(BaseModel):
    data: T
    meta: Meta


class PaginatedResponse(BaseModel):
    data: list[T]
    meta: MetaPaginated
