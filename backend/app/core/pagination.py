from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, Field, field_validator

T = TypeVar("T")


class PaginationParams(BaseModel):
    q: str | None = Field(default=None, max_length=200)
    page: int = Field(default=1, ge=1)
    page_size: int = 25

    @field_validator("page_size")
    @classmethod
    def validate_page_size(cls, value: int) -> int:
        if value not in {25, 50, 100}:
            raise ValueError("page_size deve ser 25, 50 ou 100")
        return value


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    as_of: datetime


def last_valid_page(total: int, page_size: int) -> int:
    if total <= 0:
        return 1
    return ((total - 1) // page_size) + 1
