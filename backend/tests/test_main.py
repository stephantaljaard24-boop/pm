from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


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
