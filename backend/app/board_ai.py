import json
from typing import Any

from pydantic import ValidationError

from app.ai_client import ask_openrouter_json
from app.schemas import AIChatMessagePayload, AIBoardResponse, BoardPayload


class AIResponseValidationError(Exception):
    pass


AI_BOARD_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "reply": {
            "type": "string",
            "description": "A concise response to show to the user.",
        },
        "board": {
            "anyOf": [
                {
                    "type": "object",
                    "properties": {
                        "columns": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "title": {"type": "string"},
                                    "cardIds": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                },
                                "required": ["id", "title", "cardIds"],
                                "additionalProperties": False,
                            },
                        },
                        "cards": {
                            "type": "object",
                            "additionalProperties": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "title": {"type": "string"},
                                    "details": {"type": "string"},
                                },
                                "required": ["id", "title", "details"],
                                "additionalProperties": False,
                            },
                        },
                    },
                    "required": ["columns", "cards"],
                    "additionalProperties": False,
                },
                {"type": "null"},
            ],
            "description": "Updated full board payload, or null when no board change is needed.",
        },
    },
    "required": ["reply", "board"],
    "additionalProperties": False,
}


def ask_board_ai(
    question: str,
    board: dict[str, Any],
    history: list[AIChatMessagePayload],
) -> AIBoardResponse:
    messages = build_board_ai_messages(question, board, history)
    raw_response = ask_openrouter_json(messages, AI_BOARD_RESPONSE_SCHEMA)

    try:
        response = AIBoardResponse.model_validate(raw_response)
    except ValidationError as exc:
        raise AIResponseValidationError("AI response did not match the expected schema") from exc

    if response.board is not None:
        validate_board_integrity(response.board)

    return response


def build_board_ai_messages(
    question: str,
    board: dict[str, Any],
    history: list[AIChatMessagePayload],
) -> list[dict[str, str]]:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a project management assistant for a Kanban board. "
                "Answer the user and optionally update the board. "
                "Return JSON that matches the provided schema. "
                "Use board null when no board change is needed. "
                "When changing the board, return the complete updated board. "
                "Keep existing column IDs and card IDs unless creating a new card."
            ),
        }
    ]
    messages.extend(message.model_dump() for message in history)
    messages.append(
        {
            "role": "user",
            "content": (
                f"Current board JSON:\n{json.dumps(board)}\n\n"
                f"User request:\n{question}"
            ),
        }
    )
    return messages


def validate_board_integrity(board: BoardPayload) -> None:
    column_ids = [column.id for column in board.columns]
    if len(column_ids) != len(set(column_ids)):
        raise AIResponseValidationError("AI response contained duplicate column IDs")

    card_keys = set(board.cards.keys())
    card_ids = {card.id for card in board.cards.values()}
    if card_keys != card_ids:
        raise AIResponseValidationError("AI response card keys must match card IDs")

    placed_card_ids = [
        card_id for column in board.columns for card_id in column.cardIds
    ]
    if len(placed_card_ids) != len(set(placed_card_ids)):
        raise AIResponseValidationError("AI response placed a card more than once")

    if set(placed_card_ids) != card_keys:
        raise AIResponseValidationError("AI response board columns must reference every card once")
