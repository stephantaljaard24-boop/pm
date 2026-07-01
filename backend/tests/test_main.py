from pathlib import Path

from fastapi.testclient import TestClient

from app.ai_client import OpenRouterConfigError, OpenRouterRequestError
from app.board_ai import AIResponseValidationError
from app.main import app
from app.schemas import AIBoardResponse, BoardPayload


def test_root_serves_frontend_index(tmp_path: Path, monkeypatch) -> None:
    index_path = tmp_path / "index.html"
    index_path.write_text("<html><body>Kanban Studio</body></html>", encoding="utf-8")
    monkeypatch.setenv("FRONTEND_BUILD_DIR", str(tmp_path))

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert "Kanban Studio" in response.text


def test_health_endpoint_returns_status() -> None:
    client = TestClient(app)
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "pm-backend"}


def test_ai_test_endpoint_returns_openrouter_answer(monkeypatch) -> None:
    monkeypatch.setattr("app.main.ask_openrouter", lambda prompt: "4")
    client = TestClient(app)

    response = client.get("/api/ai/test")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "model": "openai/gpt-oss-120b",
        "answer": "4",
    }


def test_ai_test_endpoint_reports_missing_api_key(monkeypatch) -> None:
    def raise_config_error(prompt: str) -> str:
        raise OpenRouterConfigError("OPENROUTER_API_KEY is not configured")

    monkeypatch.setattr("app.main.ask_openrouter", raise_config_error)
    client = TestClient(app)

    response = client.get("/api/ai/test")

    assert response.status_code == 500
    assert response.json() == {
        "status": "error",
        "message": "OPENROUTER_API_KEY is not configured",
    }


def test_ai_test_endpoint_reports_openrouter_request_error(monkeypatch) -> None:
    def raise_request_error(prompt: str) -> str:
        raise OpenRouterRequestError("OpenRouter request failed")

    monkeypatch.setattr("app.main.ask_openrouter", raise_request_error)
    client = TestClient(app)

    response = client.get("/api/ai/test")

    assert response.status_code == 502
    assert response.json() == {
        "status": "error",
        "message": "OpenRouter request failed",
    }


def test_get_board_creates_default_state_for_user(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "pm.db"))
    client = TestClient(app)

    response = client.get("/api/board/user")

    assert response.status_code == 200
    body = response.json()
    assert body["columns"][0]["title"] == "Backlog"
    assert "card-1" in body["cards"]


def test_put_board_persists_updates_for_user(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "pm.db"))
    client = TestClient(app)

    payload = {
        "columns": [
            {"id": "col-one", "title": "Updated backlog", "cardIds": ["card-1"]}
        ],
        "cards": {
            "card-1": {"id": "card-1", "title": "New card", "details": "Saved"}
        },
    }

    response = client.put("/api/board/user", json=payload)
    assert response.status_code == 200

    persisted = client.get("/api/board/user").json()
    assert persisted["columns"][0]["title"] == "Updated backlog"
    assert persisted["cards"]["card-1"]["title"] == "New card"


def test_board_ai_endpoint_returns_reply_without_board_update(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "pm.db"))
    monkeypatch.setattr(
        "app.main.ask_board_ai",
        lambda message, board, history: AIBoardResponse(reply="No changes needed.", board=None),
    )
    client = TestClient(app)

    response = client.post("/api/ai/board/user", json={"message": "Summarize this board"})

    assert response.status_code == 200
    assert response.json() == {"reply": "No changes needed.", "board": None}


def test_board_ai_endpoint_applies_valid_board_update(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "pm.db"))
    updated_board = BoardPayload(
        columns=[{"id": "col-one", "title": "Done", "cardIds": ["card-1"]}],
        cards={"card-1": {"id": "card-1", "title": "Created by AI", "details": "Saved"}},
    )
    monkeypatch.setattr(
        "app.main.ask_board_ai",
        lambda message, board, history: AIBoardResponse(reply="Created the card.", board=updated_board),
    )
    client = TestClient(app)

    response = client.post("/api/ai/board/user", json={"message": "Create a card"})

    assert response.status_code == 200
    assert response.json()["board"]["cards"]["card-1"]["title"] == "Created by AI"
    persisted = client.get("/api/board/user").json()
    assert persisted["cards"]["card-1"]["title"] == "Created by AI"


def test_board_ai_endpoint_rejects_malformed_ai_response_without_saving(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "pm.db"))
    client = TestClient(app)
    original = client.get("/api/board/user").json()

    def raise_validation_error(message, board, history):
        raise AIResponseValidationError("AI response did not match the expected schema")

    monkeypatch.setattr("app.main.ask_board_ai", raise_validation_error)

    response = client.post("/api/ai/board/user", json={"message": "Break the board"})

    assert response.status_code == 502
    assert response.json() == {
        "status": "error",
        "message": "AI response did not match the expected schema",
    }
    assert client.get("/api/board/user").json() == original
