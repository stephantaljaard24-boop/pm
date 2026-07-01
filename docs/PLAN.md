# Project plan

## Recent updates and design decisions (2026-07-01)

- Deployment: Podman-only local deployment. Containerfile and `scripts/start.*` updated for Podman usage.
- Backend: FastAPI app serves the built Next.js frontend and exposes REST endpoints. SQLite is used for persistence and the DB is initialized automatically.
- Frontend: Next.js app renders immediately from seeded `initialData`, fetches backend board in the background, and persists edits via a `saveBoard` API wrapper. Column title edits use a draft input and commit on blur/Enter to make saves deterministic.
- Testing: Unit tests (Vitest) updated and passing. Playwright E2E added for persistence; the persistence spec now uses Playwright `request` to PUT an updated board and then asserts the UI reads the persisted state.
- Container build fix: `backend/Containerfile` updated to copy `backend/app` before running `pip install --editable .` to prevent build failures.
- AI connectivity: Backend OpenRouter client added with a debug endpoint at `/api/ai/test`; start scripts now pass `.env` into Podman so the container can read `OPENROUTER_API_KEY`. Mocked backend tests pass and a manual live 2 + 2 check returned `4`.
- Board-aware AI: Backend endpoint added at `/api/ai/board/{user_id}`. It sends the current board plus user message/history to OpenRouter, requires a structured JSON response, validates optional board updates before saving, and rejects malformed AI output without changing persisted board state.
- AI chat sidebar: Frontend sidebar added to the board workspace. It sends chat prompts to the board-aware AI endpoint, displays the conversation, applies AI-generated board updates, and shows a clear error when the AI request fails.

These decisions are implemented in the repository and validated locally: the backend serves API and built frontend on http://localhost:8000 when the `pm-mvp` image is run.

## Part 1: Plan and project baseline

This phase is documentation-only. It locked in the implementation sequence, defined clear checkpoints, and captured the current frontend architecture so later work could build on it safely.

### Checklist
- [x] Review the product requirements in [AGENTS.md](../AGENTS.md)
- [x] Review the existing frontend MVP in [frontend](../frontend)
- [x] Confirm the local deployment target is Podman rather than Docker
- [x] Expand this plan into a detailed implementation checklist for each later phase
- [x] Create a frontend guidance file describing the current app structure and test setup
- [x] Present the completed plan for user review before moving to implementation

### Deliverables
- [x] A detailed plan for Parts 2 through 10, with step-by-step checklists
- [x] A frontend-specific AGENTS document covering the current architecture, key files, and how to run tests
- [x] A clear review point so the user can approve the approach before coding starts

### Success criteria
- The plan is specific enough that the next implementation step can start without major ambiguity
- The frontend guidance reflects the actual codebase rather than a generic Next.js template
- The user has a clear opportunity to review and approve the plan before any build work begins

---

## Part 2: Scaffolding the app shell

### Goal
Create the local containerized foundation so the app can run in Podman and expose both a static frontend entry point and a simple backend API.

### Checklist
- [x] Create the backend application structure under [backend](../backend)
- [x] Add a minimal FastAPI app with a health endpoint and a simple API route
- [x] Add a Podman-compatible container definition and any required build/runtime files
- [x] Add start and stop scripts under [scripts](../scripts) for Windows, macOS, and Linux
- [x] Verify that the app serves a basic hello-world response locally and that the API route responds correctly

### Tests
- [x] Run the container locally and confirm the app starts without errors
- [x] Verify the root route returns the expected static content
- [x] Verify the API endpoint returns a successful JSON response

### Success criteria
- The app can be started and stopped locally with the provided scripts
- A developer can confirm the app is reachable from the local machine without needing manual Docker-specific setup

---

## Part 3: Frontend integration and static serving

### Goal
Make the existing Kanban demo the actual application experience served at the root route, with the frontend built and served by the backend.

### Checklist
- [x] Ensure the Next.js frontend can be built for production
- [x] Configure the backend to serve the built frontend at the root route
- [x] Keep the existing Kanban board experience intact while wiring it into the deployed app
- [x] Add or refine unit and integration tests around board rendering and core interactions

### Tests
- [x] Run frontend unit tests for the Kanban logic and UI components
- [x] Run the browser-based integration suite for the board experience
- [x] Confirm the app renders the board when served through the full stack

### Success criteria
- The production build serves the board successfully at the root route
- The existing core Kanban behavior still works after integration

---

## Part 4: Fake sign-in experience

### Goal
Add a basic authentication gate so the user must log in before seeing the board.

### Checklist
- [x] Add a simple sign-in screen with the hardcoded credentials user / password
- [x] Require authentication before the board is shown
- [x] Add logout behavior and a simple session state that is easy to reason about for the MVP
- [x] Cover sign-in, access control, and logout with tests

### Tests
- [x] Verify that unauthenticated visitors are redirected or blocked from the board
- [x] Verify that valid credentials unlock the board
- [x] Verify that logging out returns the user to the sign-in state

### Success criteria
- The board is inaccessible without authentication
- The sign-in flow is simple and reliable for the MVP

---

## Part 5: Database modeling and schema proposal

### Goal
Define the data model for a multi-user-capable Kanban board and document the approach before implementation.

### Checklist
- [x] Propose a SQLite-friendly schema for users, boards, columns, and cards
- [x] Save the schema definition as JSON in the documentation folder
- [x] Document how the schema will support future multi-user growth while staying simple for the MVP
- [x] Present the schema proposal to the user for approval

### Tests
- [x] Validate that the proposed JSON schema is internally consistent
- [x] Verify the schema can represent the current board structure and future extensions

### Success criteria
- The schema is explicit and reviewable before backend persistence work begins
- The user can approve the data model before implementation

---

## Part 6: Backend persistence and API routes

### Goal
Add backend routes to read and mutate the Kanban board for a signed-in user and create the database when needed.

### Checklist
- [x] Implement SQLite initialization on startup if the database file does not exist
- [x] Create backend routes for reading and updating board state
- [x] Make the API work for a single user in the MVP while keeping the structure extensible
- [x] Add backend unit tests for the main persistence flows

### Tests
- [x] Verify the database is created automatically when missing
- [x] Verify reads and writes work correctly through the API layer
- [x] Verify invalid or empty data is handled safely

### Success criteria
- The backend can persist Kanban state without manual database setup
- Core board operations work end to end through the API

---

## Part 7: Frontend-backend integration

### Goal
Connect the frontend to the backend so the board is persistent rather than purely client-side.

### Checklist
- [x] Replace the current in-memory board state with backend-backed data loading
- [x] Send create, update, and move actions to the API
- [x] Handle loading and error states in the UI
- [x] Add end-to-end tests for the persistent board flow

### Tests
- [x] Verify the board loads from the backend on first render (frontend uses seeded data then merges backend response)
- [x] Verify edits and card moves are persisted and reflected in the UI
- [x] Verify the UI behaves correctly when the API fails

### Success criteria
- The board remains available across refreshes or app restarts for the signed-in user
- The frontend and backend behave as a single coherent product

---

## Part 8: AI connectivity

### Goal
Add a working OpenRouter-based backend integration for AI requests.

### Checklist
- [x] Add the OpenRouter client configuration and environment handling
- [x] Verify the backend can make a simple AI request such as a 2 + 2 test
- [x] Keep the initial AI integration isolated and easy to test

### Tests
- [x] Verify a simple request succeeds with the configured model and API key
- [x] Verify errors are surfaced clearly when the API key or network path is misconfigured

### Success criteria
- The backend can successfully call the configured AI model through OpenRouter
- The implementation is ready for board-aware prompts

---

## Part 9: Structured board-aware AI actions

### Goal
Allow the AI to understand the current board and optionally propose changes to it.

### Checklist
- [x] Send the current board JSON plus the user question and any conversation history to the AI
- [x] Require the AI response to use a structured output schema with a text reply and optional board updates
- [x] Validate and apply safe board updates from the AI response
- [x] Add thorough tests for normal and edge-case AI responses

### Tests
- [x] Verify a simple prompt returns a structured response
- [x] Verify valid board updates are applied correctly
- [x] Verify invalid or malformed AI output is handled safely

### Success criteria
- The AI can answer user requests while optionally modifying the board
- The backend rejects malformed AI output without corrupting board state

---

## Part 10: AI chat sidebar experience

### Goal
Provide a polished UI for chatting with the AI and let AI-driven updates refresh the board automatically.

### Checklist
- [x] Add a sidebar chat panel to the app shell
- [x] Send user prompts to the backend and show the AI responses in the UI
- [x] Apply AI-generated board updates and refresh the board automatically
- [x] Keep the experience simple and visually aligned with the existing design system

### Tests
- [x] Verify chat messages render correctly
- [x] Verify AI-driven board updates are reflected in the UI
- [x] Verify the app remains usable when the AI response contains no board changes

### Success criteria
- The user can chat with the AI from the app and see board updates when appropriate
- The experience feels cohesive with the current Kanban UI
