from typing import Literal

from pydantic import BaseModel, Field


class CardPayload(BaseModel):
    id: str
    title: str
    details: str


class ColumnPayload(BaseModel):
    id: str
    title: str
    cardIds: list[str]


class BoardPayload(BaseModel):
    columns: list[ColumnPayload]
    cards: dict[str, CardPayload]


class AIChatMessagePayload(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class AIBoardRequest(BaseModel):
    message: str
    history: list[AIChatMessagePayload] = Field(default_factory=list)


class AIBoardResponse(BaseModel):
    reply: str
    board: BoardPayload | None
