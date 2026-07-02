# Code Review — 2026-07-02

Full-repository review of the Project Management MVP (backend, frontend, scripts,
docs, packaging). Findings are ranked by severity with a concrete failure
scenario and a recommended action for each.

## Summary

| # | Severity | Area | Finding |
|---|----------|------|---------|
| 1 | High — **Fixed** | Backend persistence | Every board request opens a redundant, never-explicitly-closed SQLite connection and re-runs schema DDL |
| 2 | High — **Fixed** | Frontend state | Initial board fetch can silently overwrite in-flight local edits |
| 3 | Medium | Frontend UX | Board save failures (PUT) are swallowed — UI shows unsaved changes as if persisted |
| 4 | Medium | Dev workflow | No CORS config means `npm run dev` cannot talk to a locally running backend |
| 5 | Medium | Repo hygiene | Default local SQLite file (`backend/pm.db`) is not gitignored |
| 6 | Low | Backend | `check_endpoints.py` uses a stale import path and will fail to run |
| 7 | Info | Security posture | API has no authorization — the frontend login is cosmetic only |

---

## 1. Redundant, unclosed SQLite connections on every request (High)

**File:** `backend/app/persistence.py:22-57`

`get_board_data` and `save_board_data` both unconditionally call
`initialize_database()` before doing their real work. Each of those two
functions opens its **own** connection via `get_connection()`:

```python
def get_board_data(user_id: str) -> dict[str, Any]:
    initialize_database()          # opens + "closes" connection #1
    with get_connection() as connection:   # opens connection #2
        row = connection.execute(...).fetchone()
    ...
```

Two problems:

- `with get_connection() as connection:` only wraps the **transaction**
  (`sqlite3.Connection.__exit__` commits/rolls back) — it does not call
  `connection.close()`. The file handle is only released whenever CPython's
  reference counting happens to collect the local `connection` object. This
  works today because CPython closes it almost immediately, but it's a
  well-known footgun: it produces `ResourceWarning`s under `-W`, and breaks
  silently under PyPy or any GC that doesn't refcount.
- Every single `GET`/`PUT /api/board/{user_id}` and every AI board turn opens
  **two** SQLite connections and re-issues `CREATE TABLE IF NOT EXISTS` when
  it only needs one connection and the table almost certainly already exists.

**Failure scenario:** under any real request load, this doubles SQLite
connection churn per request and leaves connection lifetime to GC timing
rather than explicit control — this is fragile now and will misbehave if the
interpreter or SQLite driver changes.

**Action:**
- Run `initialize_database()` once at FastAPI startup (`@app.on_event("startup")`
  or a lifespan handler) instead of on every call.
- Explicitly close connections, e.g. `with contextlib.closing(get_connection()) as connection:`.

**Fix applied:** `get_connection()` now issues `CREATE TABLE IF NOT EXISTS`
inline as part of connection setup (the separate `initialize_database()` /
second connection is gone), and `get_board_data`/`save_board_data` each open
exactly one connection, closed explicitly in a `finally` block. Verified via
`python -m pytest backend/tests` (14/14 passing).

---

## 2. Initial board fetch can clobber in-flight local edits (High)

**File:** `frontend/src/components/KanbanBoard.tsx:26-44`

```tsx
const [board, setBoard] = useState<BoardData>(() => initialData);
...
useEffect(() => {
  const loadBoard = async () => {
    try {
      const fetchedBoard = await fetchBoard("user");
      setBoard(fetchedBoard);          // unconditional overwrite
    } catch (error) {
      console.error(error);
      setBoard(initialData);
    }
  };
  void loadBoard();
}, []);
```

The board renders immediately from seeded `initialData`, then a background
fetch replaces the entire board state once it resolves. If the user adds a
card, renames a column, or drags a card in that window, `setBoard(fetchedBoard)`
silently discards that local change (the local mutation triggers its own
`persistBoard` save, but the later fetch response — which does not include
that change yet, or resolves after a race — wins and overwrites local state
with no merge and no warning).

**Failure scenario:** user opens the app and immediately adds a card before
the background board fetch resolves (plausible on a slow network/backend
cold start) → their card disappears from the UI with no error, even though a
`saveBoard` PUT for it may have already fired.

**Action:** guard the fetch so it doesn't apply once the user has interacted
(e.g. track a `hasLocalChanges` ref and skip `setBoard` if set), or block
interaction until the initial load completes, or merge instead of replace.

**Fix applied:** added a `hasLocalChanges` ref, set at the start of
`persistBoard` (i.e. the moment any mutation begins saving). The background
`loadBoard` effect now only calls `setBoard(fetchedBoard)` if no local change
has started yet, and the fetch-error fallback that used to reset the board to
`initialData` (also clobbering local edits) was removed. Verified via
`npm run test:unit` (12/12 passing).

---

## 3. Board save failures are invisible to the user (Medium)

**File:** `frontend/src/components/KanbanBoard.tsx:58-64`

```tsx
const persistBoard = async (nextBoard: BoardData) => {
  try {
    await saveBoard("user", nextBoard);
  } catch (error) {
    console.error(error);
  }
};
```

Every mutation (drag, rename, add, delete) updates local state optimistically
and fires `persistBoard` in the background. If the `PUT` fails (backend down,
network blip), the error is only logged to the console — the board still
shows the change as applied, and nothing tells the user the edit wasn't
persisted. Contrast with `AIChatSidebar`, which does surface errors to the
user via `chatError`.

**Failure scenario:** backend is briefly unreachable while a user renames a
column; the UI shows the new name as if saved, but the next reload reverts it
with no explanation.

**Action:** surface persistence failures in the UI (banner/toast), matching
the pattern already used for AI chat errors.

---

## 4. No CORS configuration — `npm run dev` can't reach the backend (Medium)

**Files:** `backend/app/main.py` (no `CORSMiddleware`), `frontend/src/lib/api.ts:16`

`API_BASE_URL` defaults to `http://localhost:8000` regardless of where the
frontend is served from, and the README documents `npm run dev` (port 3000)
as a valid local workflow. But the FastAPI app registers no CORS middleware,
so any cross-origin call from `localhost:3000` to `localhost:8000` will be
blocked by the browser.

**Failure scenario:** a contributor runs `cd frontend && npm run dev` per the
README/AGENTS docs and expects a working app against a locally running
backend. `fetchBoard` fails and is silently swallowed (falls back to seed
data, masking the real cause), while `saveBoard` and `chatWithBoardAi` throw
visible errors — the AI sidebar and persistence appear broken with no
indication it's a CORS issue rather than a backend bug.

**Action:** either add `CORSMiddleware` allowing `http://localhost:3000` for
local development, or explicitly document that `npm run dev` is frontend-UI
iteration only and the full stack must be exercised via the Podman container.

---

## 5. Default local SQLite file is not gitignored (Medium)

**File:** `.gitignore` (root), `backend/app/persistence.py:7`

`DEFAULT_DATABASE_PATH` is `backend/pm.db`, used whenever `DATABASE_PATH` is
unset (e.g. running the backend directly outside the container). The root
`.gitignore` has no `*.db` / `pm.db` rule (verified: `git check-ignore -v
backend/pm.db` reports not ignored).

**Failure scenario:** a developer runs the backend locally for debugging,
`backend/pm.db` is created, and a later `git add -A` / `git add .` stages the
local board database (containing whatever board data happened to be saved)
into a commit.

**Action:** add `backend/pm.db` (or a general `*.db`) to `.gitignore`.

---

## 6. `check_endpoints.py` uses a stale import path (Low)

**File:** `backend/check_endpoints.py:1`

```python
from backend.app.main import app
```

Every other entry point (`backend/tests/*.py`, `Containerfile`'s
`uvicorn app.main:app`) imports the package as `app.main`, matching
`pyproject.toml`'s `packages = ["app"]` — there is no top-level `backend`
package. This script will raise `ModuleNotFoundError: No module named
'backend'` unless run from an unusual working directory/PYTHONPATH not used
anywhere else in the project.

**Action:** fix the import to `from app.main import app` (run from
`backend/`, same as the test suite), or delete the script if it's stale and
superseded by `backend/tests/test_main.py`.

---

## 7. API has no authorization (Info — known MVP limitation, restated)

**Files:** `backend/app/main.py:45-75`, `frontend/src/app/page.tsx`

Sign-in is entirely client-side state (`isAuthenticated` in `page.tsx`) with
hardcoded credentials; the backend applies no authentication or authorization
to `/api/board/{user_id}` or `/api/ai/board/{user_id}`. Anyone with network
access to the backend can read/write any `user_id`'s board or trigger AI
calls (spending the configured `OPENROUTER_API_KEY` budget) without ever
touching the login screen.

This is already called out as an explicit MVP limitation in `AGENTS.md`, so
it is not a regression — restating it here as a reminder that this app must
not be exposed beyond a trusted local/internal network as-is.

**Action:** none required for the MVP; flag before any deployment beyond
local/trusted use.
