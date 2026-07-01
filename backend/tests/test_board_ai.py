import pytest

from app.ai_client import OpenRouterRequestError, ask_openrouter_json
from app.board_ai import (
    AIResponseValidationError,
    ask_board_ai,
    validate_board_integrity,
)
from app.schemas import BoardPayload


def test_ask_board_ai_rejects_invalid_ai_schema(monkeypatch) -> None:
    monkeypatch.setattr("app.board_ai.ask_openrouter_json", lambda messages, schema: {"board": None})

    with pytest.raises(AIResponseValidationError):
        ask_board_ai("Summarize", {"columns": [], "cards": {}}, [])


def test_ask_board_ai_rejects_invalid_board_update(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.board_ai.ask_openrouter_json",
        lambda messages, schema: {
            "reply": "Moved it.",
            "board": {
                "columns": [{"id": "col-one", "title": "Backlog", "cardIds": []}],
                "cards": {"card-1": {"id": "card-1", "title": "Card", "details": ""}},
            },
        },
    )

    with pytest.raises(AIResponseValidationError):
        ask_board_ai("Move the card", {"columns": [], "cards": {}}, [])


def test_validate_board_integrity_accepts_consistent_board() -> None:
    board = BoardPayload(
        columns=[{"id": "col-one", "title": "Backlog", "cardIds": ["card-1"]}],
        cards={"card-1": {"id": "card-1", "title": "Card", "details": ""}},
    )

    validate_board_integrity(board)


def test_ask_openrouter_json_rejects_invalid_json(monkeypatch) -> None:
    monkeypatch.setattr("app.ai_client.get_openrouter_chat_completion", lambda messages, schema: "not json")

    with pytest.raises(OpenRouterRequestError):
        ask_openrouter_json([], {})
