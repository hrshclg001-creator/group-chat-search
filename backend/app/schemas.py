"""Validated public search and corpus-statistics contracts."""

from typing import List, Literal, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    query: str = Field(strict=True, min_length=1, max_length=2000)
    top_k: int = Field(default=5, strict=True, ge=1, le=50)

    @field_validator('query')
    @classmethod
    def reject_blank_query(cls, value):
        if not value.strip():
            raise ValueError('query must contain non-whitespace text')
        return value


class MessageResponse(BaseModel):
    id: str
    sender: str
    timestamp: str
    text: str


class InterpretedQuery(BaseModel):
    raw_query: str
    person: Optional[str]
    person_mode: Literal['none', 'bonus', 'filter']
    person_candidates: List[str]
    start_date: Optional[str]
    end_date: Optional[str]
    hour_range: Optional[Tuple[int, int]]
    intent: str
    reference_date: str
    timezone: str
    warnings: List[str]
    explanations: List[str]


class SearchResultResponse(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)

    matching_message: MessageResponse
    previous_messages: List[MessageResponse] = Field(max_length=3)
    next_messages: List[MessageResponse] = Field(max_length=3)
    search_score: float
    semantic_score: float
    contextual_score: float
    lexical_score: float
    query_metadata: InterpretedQuery
    rank: int = Field(ge=1)


class SearchResponse(BaseModel):
    query: str
    interpreted_query: InterpretedQuery
    search_time_ms: float = Field(ge=0, allow_inf_nan=False)
    results: List[SearchResultResponse]


class DateRange(BaseModel):
    start: str
    end: str


class StatsResponse(BaseModel):
    message_count: int
    participant_count: int
    date_range: DateRange
    reference_date: str
    timezone: str
