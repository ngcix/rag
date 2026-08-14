"""HTTP request and response schemas."""

from typing import Any

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    source: str
    collection: str = "default"
    replace: bool = False


class QueryRequest(BaseModel):
    text: str = Field(min_length=1)
    collection: str = "default"
    top_k: int = Field(default=5, ge=1, le=100)
    hybrid: bool = False


class QueryResponse(BaseModel):
    results: list[dict[str, Any]]


class CollectionResponse(BaseModel):
    collection: str
    details: dict[str, Any]
