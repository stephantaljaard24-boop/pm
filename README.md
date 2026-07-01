# Project Management MVP

Local project management app with a FastAPI backend, static Next.js frontend, SQLite persistence, and OpenRouter-powered board assistant.

## What It Does

- Signs in with hardcoded MVP credentials: `user` / `password`.
- Shows one persisted Kanban board for the signed-in user.
- Supports fixed columns that can be renamed.
- Supports creating, deleting, and drag-moving cards.
- Provides an AI chat sidebar that can answer questions about the board and apply validated board updates.

## Architecture

- `frontend/`: Next.js static app. The board UI lives in `src/components/KanbanBoard.tsx`; AI chat UI lives in `src/components/AIChatSidebar.tsx`.
- `backend/`: FastAPI app. It serves the built frontend at `/`, exposes API routes under `/api`, stores board state in SQLite, and calls OpenRouter.
- `scripts/`: Podman start and stop scripts for Windows and Unix-like shells.
- `docs/`: project plan and database schema documentation.

The backend stores the MVP board as JSON in SQLite. This is intentionally simple for the MVP while the documented schema in `docs/database-schema.json` captures a future normalized multi-user model.

## Environment

Create `.env` in the project root:

```text
OPENROUTER_API_KEY=your_openrouter_key
```

Optional backend environment variables:

- `DATABASE_PATH`: SQLite file path. Defaults to `backend/pm.db` locally and `/app/pm.db` inside the container.
- `FRONTEND_BUILD_DIR`: static Next.js output directory. The container sets this to `/app/frontend/out`.

Do not commit `.env`.

## Run Locally With Podman

Windows:

```powershell
./scripts/start.ps1
```

macOS/Linux:

```bash
./scripts/start.sh
```

Open:

```text
http://localhost:8000
```

Stop:

```powershell
./scripts/stop.ps1
```

or:

```bash
./scripts/stop.sh
```

## API

- `GET /api/health`: backend health check.
- `GET /api/board/{user_id}`: read persisted board state.
- `PUT /api/board/{user_id}`: replace persisted board state.
- `GET /api/ai/test`: simple OpenRouter connectivity check.
- `POST /api/ai/board/{user_id}`: send a message, history, and current board context to AI. Returns a text reply and optional validated board update.

## Tests

Backend:

```powershell
python -m pytest backend/tests
```

Frontend:

```powershell
cd frontend
npm run test:unit
npm run build
```

If pytest hits Windows temp/cache permissions, rerun with a writable workspace temp/cache path.

## Deploy Elsewhere

The app is packaged as one container image from `backend/Containerfile`. To deploy in another local or server environment:

1. Install Podman or another OCI-compatible container runtime.
2. Provide `OPENROUTER_API_KEY` as an environment variable or env file.
3. Build from the repo root:

```bash
podman build -f backend/Containerfile -t pm-mvp .
```

4. Run:

```bash
podman run --rm -d --name pm-mvp --env-file .env -p 8000:8000 pm-mvp
```

For durable data outside the container, mount a host directory and set `DATABASE_PATH` to a path inside that mount, for example `/data/pm.db`.
