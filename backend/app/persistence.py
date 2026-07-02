import json
import os
import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_DATABASE_PATH = Path(__file__).resolve().parent.parent / "pm.db"


def get_database_path() -> Path:
    return Path(os.getenv("DATABASE_PATH", str(DEFAULT_DATABASE_PATH))).resolve()


def get_connection() -> sqlite3.Connection:
    db_path = get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS boards (
            user_id TEXT PRIMARY KEY,
            board_json TEXT NOT NULL
        )
        """
    )
    return connection


def get_board_data(user_id: str) -> dict[str, Any]:
    connection = get_connection()
    try:
        with connection:
            row = connection.execute(
                "SELECT board_json FROM boards WHERE user_id = ?",
                (user_id,),
            ).fetchone()
    finally:
        connection.close()

    if row is None:
        return default_board_payload()

    return json.loads(row["board_json"])


def save_board_data(user_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    board_json = json.dumps(payload)
    connection = get_connection()
    try:
        with connection:
            connection.execute(
                "INSERT INTO boards(user_id, board_json) VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE SET board_json = excluded.board_json",
                (user_id, board_json),
            )
    finally:
        connection.close()

    return payload


def default_board_payload() -> dict[str, Any]:
    return {
        "columns": [
            {"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1", "card-2"]},
            {"id": "col-discovery", "title": "Discovery", "cardIds": ["card-3"]},
            {"id": "col-progress", "title": "In Progress", "cardIds": ["card-4", "card-5"]},
            {"id": "col-review", "title": "Review", "cardIds": ["card-6"]},
            {"id": "col-done", "title": "Done", "cardIds": ["card-7", "card-8"]},
        ],
        "cards": {
            "card-1": {"id": "card-1", "title": "Align roadmap themes", "details": "Draft quarterly themes with impact statements and metrics."},
            "card-2": {"id": "card-2", "title": "Gather customer signals", "details": "Review support tags, sales notes, and churn feedback."},
            "card-3": {"id": "card-3", "title": "Prototype analytics view", "details": "Sketch initial dashboard layout and key drill-downs."},
            "card-4": {"id": "card-4", "title": "Refine status language", "details": "Standardize column labels and tone across the board."},
            "card-5": {"id": "card-5", "title": "Design card layout", "details": "Add hierarchy and spacing for scanning dense lists."},
            "card-6": {"id": "card-6", "title": "QA micro-interactions", "details": "Verify hover, focus, and loading states."},
            "card-7": {"id": "card-7", "title": "Ship marketing page", "details": "Final copy approved and asset pack delivered."},
            "card-8": {"id": "card-8", "title": "Close onboarding sprint", "details": "Document release notes and share internally."},
        },
    }
