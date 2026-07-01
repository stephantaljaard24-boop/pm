# Backend guidance

## Role

The backend is a FastAPI app that:
- Serves the static Next.js build at `/`.
- Exposes JSON API routes under `/api`.
- Persists the MVP board in SQLite.
- Calls OpenRouter for simple and board-aware AI requests.

## Key files

- `app/main.py`: FastAPI app, API routes, and static frontend serving.
- `app/persistence.py`: SQLite database path handling, initialization, read, and save.
- `app/schemas.py`: Pydantic request and response models.
- `app/ai_client.py`: OpenRouter client configuration and JSON response handling.
- `app/board_ai.py`: board-aware prompt construction, structured response schema, and board integrity validation.
- `tests/`: pytest coverage for API routes, persistence, AI response validation, and error handling.
- `Containerfile`: multi-stage container build for frontend plus backend runtime.

## API routes

- `GET /api/health`: returns backend health.
- `GET /api/board/{user_id}`: returns persisted board JSON or a default board.
- `PUT /api/board/{user_id}`: replaces the persisted board.
- `GET /api/ai/test`: verifies OpenRouter connectivity with a simple prompt.
- `POST /api/ai/board/{user_id}`: sends board context and user message to AI, then persists a valid returned board update.

## Environment

- `OPENROUTER_API_KEY`: required for AI calls.
- `DATABASE_PATH`: optional SQLite path override.
- `FRONTEND_BUILD_DIR`: optional static frontend build directory override.

## Testing

Run backend tests from the repo root:

```powershell
python -m pytest backend/tests
```

If Windows temp/cache permissions fail, set `TEMP`, `TMP`, and pytest `cache_dir` to a writable workspace folder for that test run.

## Implementation notes

- Keep persistence simple for the MVP. The current implementation stores a full board JSON document.
- Validate AI board updates before saving. Invalid or malformed AI output must not corrupt persisted state.
- Do not log or expose `OPENROUTER_API_KEY`.
- Keep board-aware AI logic out of `main.py`; route handlers should stay thin.
