from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List

class PageParams(BaseModel):
    page: int = Field(1, ge=1) 
    size: int = Field(10, ge=1, le=100)

# T stands for "Type". It's a variable.
T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]  # <--- This is the magic. It's a list of "Whatever"
    total: int
    page: int
    size: int
    pages: int