from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from vitalx.types.query import Period, Placeholder, Query, QueryConfig


class RelativeTimeframe(BaseModel):
    type: Literal["relative"]
    anchor: date
    past: Period


Timeframe = RelativeTimeframe | Placeholder


class QueryBatch(BaseModel):
    timeframe: Timeframe
    queries: list[Query]
    config: QueryConfig = Field(default_factory=lambda: QueryConfig())

    @model_validator(mode="before")
    @classmethod
    def validate_queries(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            return values

        # compatibility with SDK 0.1.x or earlier
        if "queries" not in values and (queries := values.pop("instructions", None)):
            values["queries"] = queries

        return values
