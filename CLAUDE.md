# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Local Project Management MVP: a single-board Kanban app with a FastAPI backend, a Next.js static frontend, SQLite persistence, and an OpenRouter-powered AI chat sidebar that can read and edit the board. See `AGENTS.md` for the full product/decision record and `docs/PLAN.md` for implementation history — read both before making non-trivial changes.

## Commands

Backend tests:
```powershell
python -m pytest backend/tests
```
(If pytest hits Windows temp/cache permission errors, rerun with a writable workspace temp/cache path.)

Frontend (run from `frontend/`):
```powershell
npm run test:unit        # vitest run
npm run test:unit:watch  # vitest watch mode
npm run test:e2e         # playwright
npm run test:all         # unit then e2e
npm run build             # next build (static export to frontend/out)
npm run lint
npm run dev                # next dev, local iteration only
```
Run a single vitest file: `npx vitest run src/lib/kanban.test.ts`.

Run the full app locally via Podman (builds the Containerfile, serves everything from one container on `http://localhost:8000`):
```powershell
./scripts/start.ps1   # ./scripts/start.sh on macOS/Linux
./scripts/stop.ps1    # ./scripts/stop.sh on macOS/Linux
```

## Architecture

- The backend serves the built frontend as static files at `/` and exposes JSON API routes under `/api` — there is no separate frontend server in production. `backend/app/main.py` owns both concerns: `read_root` / `serve_frontend` serve `frontend/out` (path set by `FRONTEND_BUILD_DIR`, defaults to `../../frontend/out` relative to `main.py`), while `/api/*` routes handle board CRUD and AI chat.
- Board state is a single JSON blob per `user_id`, stored in a SQLite table (`boards`) with `board_json` as one TEXT column — not a normalized schema. `backend/app/persistence.py` handles read/write and lazily creates the table and a default board. `docs/database-schema.json` documents an intended future normalized multi-user schema; do not treat it as the current shape.
- `backend/app/schemas.py` (Pydantic) and `frontend/src/lib/api.ts` (TypeScript types) define the same `BoardPayload` shape (`columns: {id, title, cardIds}[]`, `cards: Record<id, {id, title, details}>`) independently — when changing the board shape, update both, plus the JSON schema in `board_ai.py` and `frontend/src/lib/kanban.ts`'s `BoardData`.
- AI chat flow: frontend sends `{message, history}` to `POST /api/ai/board/{user_id}` → `board_ai.ask_board_ai` builds a prompt embedding the current board JSON, calls `ai_client.ask_openrouter_json` with a strict JSON schema (`AI_BOARD_RESPONSE_SCHEMA`) → response is validated against Pydantic models, then `validate_board_integrity` checks structural invariants (no duplicate column/card IDs, every card placed exactly once, card map keys match card IDs) → if a board update is present it's persisted immediately and returned. Any failure at the OpenRouter call, JSON parsing, schema validation, or integrity check surfaces as a specific exception type (`OpenRouterConfigError`, `OpenRouterRequestError`, `AIResponseValidationError`) mapped to an HTTP error response in `main.py`.
- OpenRouter access is centralized in `backend/app/ai_client.py` (`OPENROUTER_MODEL = "openai/gpt-oss-120b"`); `OPENROUTER_API_KEY` comes from the environment / root `.env` (never commit it).
- Frontend drag-and-drop and card/column mutation logic lives in `frontend/src/lib/kanban.ts` (pure functions like `moveCard`, `createId`) separate from `KanbanBoard.tsx`, which wires that logic to `@dnd-kit` and to the API client in `lib/api.ts`.
- Auth is a hardcoded frontend-only check (`user` / `password`) — there is no real auth boundary; don't add server-side auth assumptions without an explicit decision.
- Packaging: `backend/Containerfile` is a multi-stage build — Node stage runs `next build` (static export) into `frontend/out`, then a `python:3.13-slim` stage installs the backend with `uv` and copies the static export in. The app is always run as one container image; there's no separate dev-mode container workflow described beyond `npm run dev` / running the backend directly.

## Coding standards (from AGENTS.md)

- Keep it simple: never over-engineer, no unnecessary defensive programming, no extra features beyond what's requested.
- No emojis, anywhere.
- When debugging, find the root cause before applying a fix — don't guess-and-check.
- Colors: Accent Yellow `#ecad0a`, Blue Primary `#209dd7`, Purple Secondary `#753991`, Dark Navy `#032147`, Gray Text `#888888`.
