import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

from app.persistence import get_board_data, save_board_data
from app.schemas import BoardPayload

app = FastAPI(title="Project Management MVP Backend")

DEFAULT_FRONTEND_BUILD_DIR = (
    Path(__file__).resolve().parent.parent.parent / "frontend" / "out"
)


def get_frontend_build_dir() -> Path:
    return Path(os.getenv("FRONTEND_BUILD_DIR", str(DEFAULT_FRONTEND_BUILD_DIR))).resolve()


@app.get("/api/health")
def health_check() -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "pm-backend"})


@app.get("/api/board/{user_id}")
def get_board(user_id: str) -> JSONResponse:
    board = get_board_data(user_id)
    return JSONResponse(board)


@app.put("/api/board/{user_id}")
def put_board(user_id: str, payload: BoardPayload) -> JSONResponse:
    save_board_data(user_id, payload.model_dump())
    return JSONResponse(payload.model_dump())


@app.get("/", response_model=None)
def read_root() -> FileResponse | HTMLResponse:
    index_path = get_frontend_build_dir() / "index.html"
    if index_path.is_file():
        return FileResponse(index_path)

    return HTMLResponse(
        "<html><body><h1>Project Management MVP</h1><p>The frontend build is not available yet.</p></body></html>"
    )


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

    return HTMLResponse(
        "<html><body><h1>Project Management MVP</h1><p>The frontend build is not available yet.</p></body></html>"
    )
