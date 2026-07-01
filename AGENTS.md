# Project Management MVP

## Current Product

This repository contains a local Project Management MVP web app.

Implemented behavior:
- A user signs in with hardcoded MVP credentials: `user` / `password`.
- After sign-in, the user sees one Kanban board.
- The Kanban board has fixed columns that can be renamed.
- Cards can be created, deleted, and moved with drag and drop.
- Board state is persisted in SQLite through the backend API.
- An AI chat sidebar can answer board-aware questions and apply validated board updates.

## MVP Limitations

- Authentication is frontend-only and hardcoded for the MVP.
- There is one board for the signed-in user.
- The current SQLite implementation stores the board as JSON for simplicity.
- `docs/database-schema.json` documents the future normalized multi-user schema.
- The app is intended to run locally in a Podman container.

## Technical Decisions

- Next.js frontend exported as a static site.
- Python FastAPI backend serves the static Next.js site at `/`.
- FastAPI exposes REST endpoints under `/api`.
- Everything is packaged into a Podman-compatible container image.
- Use `uv` as the Python package installer in the container.
- Use OpenRouter for AI calls. `OPENROUTER_API_KEY` is read from `.env` or the runtime environment.
- Use `openai/gpt-oss-120b` as the model
- Use SQLite for local persistence, creating a database if it does not exist.
- Start and stop scripts live in `scripts/`.

## Key Files

- `README.md`: setup, run, test, and deployment instructions.
- `docs/PLAN.md`: implementation history and current project plan.
- `docs/database-schema.json`: proposed future normalized database schema.
- `backend/app/main.py`: FastAPI app, static frontend serving, and API routes.
- `backend/app/persistence.py`: SQLite persistence.
- `backend/app/ai_client.py`: OpenRouter client.
- `backend/app/board_ai.py`: board-aware AI prompt, structured response, and validation logic.
- `frontend/src/components/KanbanBoard.tsx`: board state and workspace layout.
- `frontend/src/components/AIChatSidebar.tsx`: AI chat UI.
- `frontend/src/lib/api.ts`: frontend API wrappers.

## Color Scheme

- Accent Yellow: `#ecad0a` - accent lines, highlights
- Blue Primary: `#209dd7` - links, key sections
- Purple Secondary: `#753991` - submit buttons, important actions
- Dark Navy: `#032147` - main headings
- Gray Text: `#888888` - supporting text, labels

## Coding standards

1. Use latest versions of libraries and idiomatic approaches as of today.
2. Keep it simple. NEVER over-engineer, ALWAYS simplify, NO unnecessary defensive programming. No extra features unless explicitly requested.
3. Be concise. Keep README minimal. IMPORTANT: no emojis ever
4. When hitting issues, always identify root cause before trying a fix. Do not guess. Prove with evidence, then fix the root cause.

## Working documentation

All documents for planning and executing this project will be in the docs/ directory.
Please review the docs/PLAN.md document before proceeding.
