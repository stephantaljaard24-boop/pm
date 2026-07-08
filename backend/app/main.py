import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

from app.ai_client import (
    OPENROUTER_MODEL,
    OpenRouterConfigError,
    OpenRouterRequestError,
    ask_openrouter,
)
from app.board_ai import AIResponseValidationError, ask_board_ai
from app.persistence import get_board_data, save_board_data
from app.schemas import AIBoardRequest, BoardPayload

app = FastAPI(title="Project Management MVP Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULT_FRONTEND_BUILD_DIR = (
    Path(__file__).resolve().parent.parent.parent / "frontend" / "out"
)

FRONTEND_UNAVAILABLE_HTML = (
    "<html><body><h1>Project Management MVP</h1>"
    "<p>The frontend build is not available yet.</p></body></html>"
)


def get_frontend_build_dir() -> Path:
    return Path(os.getenv("FRONTEND_BUILD_DIR", str(DEFAULT_FRONTEND_BUILD_DIR))).resolve()


@app.get("/api/health")
def health_check() -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "pm-backend"})


@app.get("/api/ai/test")
def test_ai_connection() -> JSONResponse:
    try:
        answer = ask_openrouter("What is 2 + 2? Reply with only the number.")
    except OpenRouterConfigError as exc:
        return JSONResponse({"status": "error", "message": str(exc)}, status_code=500)
    except OpenRouterRequestError as exc:
        return JSONResponse({"status": "error", "message": str(exc)}, status_code=502)

    return JSONResponse({"status": "ok", "model": OPENROUTER_MODEL, "answer": answer})


@app.get("/api/board/{user_id}")
def get_board(user_id: str) -> JSONResponse:
    board = get_board_data(user_id)
    return JSONResponse(board)


@app.put("/api/board/{user_id}")
def put_board(user_id: str, payload: BoardPayload) -> JSONResponse:
    save_board_data(user_id, payload.model_dump())
    return JSONResponse(payload.model_dump())


@app.post("/api/ai/board/{user_id}")
def chat_with_board_ai(user_id: str, payload: AIBoardRequest) -> JSONResponse:
    board = get_board_data(user_id)

    try:
        ai_response = ask_board_ai(payload.message, board, payload.history)
    except OpenRouterConfigError as exc:
        return JSONResponse({"status": "error", "message": str(exc)}, status_code=500)
    except (OpenRouterRequestError, AIResponseValidationError) as exc:
        return JSONResponse({"status": "error", "message": str(exc)}, status_code=502)

    updated_board = None
    if ai_response.board is not None:
        updated_board = ai_response.board.model_dump()
        save_board_data(user_id, updated_board)

    return JSONResponse({"reply": ai_response.reply, "board": updated_board})


@app.get("/", response_model=None)
def read_root() -> FileResponse | HTMLResponse:
    return serve_frontend("")


@app.get("/{full_path:path}", response_model=None)
def serve_frontend(full_path: str) -> FileResponse | HTMLResponse:
    if full_path.startswith("api/"):
        return HTMLResponse("<html><body>Not found</body></html>", status_code=404)

    build_dir = get_frontend_build_dir()
    candidate = (build_dir / full_path.lstrip("/")).resolve()

    try:
        candidate.relative_to(build_dir)
    except ValueError:
        return HTMLResponse("<html><body>Invalid frontend path</body></html>", status_code=400)

    if candidate.is_file():
        return FileResponse(candidate)

    index_path = build_dir / "index.html"
    if index_path.is_file():
        return FileResponse(index_path)

    return HTMLResponse(FRONTEND_UNAVAILABLE_HTML)
