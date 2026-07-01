# Project plan

## Recent updates and design decisions (2026-07-01)

- Deployment: Podman-only local deployment. Containerfile and `scripts/start.*` updated for Podman usage.
- Backend: FastAPI app serves the built Next.js frontend and exposes REST endpoints. SQLite is used for persistence and the DB is initialized automatically.
- Frontend: Next.js app renders immediately from seeded `initialData`, fetches backend board in the background, and persists edits via a `saveBoard` API wrapper. Column title edits use a draft input and commit on blur/Enter to make saves deterministic.
- Testing: Unit tests (Vitest) updated and passing. Playwright E2E added for persistence; the persistence spec now uses Playwright `request` to PUT an updated board and then asserts the UI reads the persisted state.
- Container build fix: `backend/Containerfile` updated to copy `backend/app` before running `pip install --editable .` to prevent build failures.

These decisions are implemented in the repository and validated locally: the backend serves API and built frontend on http://localhost:8000 when the `pm-mvp` image is run.

## Part 1: Plan and project baseline

This phase is documentation-only. The goal is to lock in the implementation sequence, define clear checkpoints, and capture the current frontend architecture so later work can build on it safely.

### Checklist
- [x] Review the product requirements in [AGENTS.md](../AGENTS.md)
- [x] Review the existing frontend MVP in [frontend](../frontend)
- [x] Confirm the local deployment target is Podman rather than Docker
- [ ] Expand this plan into a detailed implementation checklist for each later phase
- [ ] Create a frontend guidance file describing the current app structure and test setup
- [ ] Present the completed plan for user review before moving to implementation

### Deliverables
- [ ] A detailed plan for Parts 2 through 10, with step-by-step checklists
- [ ] A frontend-specific AGENTS document covering the current architecture, key files, and how to run tests
- [ ] A clear review point so the user can approve the approach before coding starts

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
- [ ] Run the container locally and confirm the app starts without errors
- [ ] Verify the root route returns the expected static content
- [ ] Verify the API endpoint returns a successful JSON response

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
- [ ] Run frontend unit tests for the Kanban logic and UI components
- [ ] Run the browser-based integration suite for the board experience
- [ ] Confirm the app renders the board when served through the full stack

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
- [ ] Verify that unauthenticated visitors are redirected or blocked from the board
- [ ] Verify that valid credentials unlock the board
- [ ] Verify that logging out returns the user to the sign-in state

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
- [ ] Present the schema proposal to the user for approval

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
- [ ] Verify the database is created automatically when missing
- [ ] Verify reads and writes work correctly through the API layer
- [ ] Verify invalid or empty data is handled safely

### Success criteria
- The backend can persist Kanban state without manual database setup
- Core board operations work end to end through the API

---

## Part 7: Frontend-backend integration

### Goal
Connect the frontend to the backend so the board is persistent rather than purely client-side.

### Checklist
- [x] Replace the current in-memory board state with backend-backed data loading
- [x] Send create, update, and move actions to the API (basic flows implemented; create/move test coverage remains)
- [ ] Handle loading and error states in the UI (basic graceful fallback implemented; UI-level states can be improved)
- [x] Add end-to-end tests for the persistent board flow (rename persistence test added; create/move tests to follow)

### Tests
- [x] Verify the board loads from the backend on first render (frontend uses seeded data then merges backend response)
- [x] Verify edits and card moves are persisted and reflected in the UI (rename/edit flows validated; move/create flows need E2E tests)
- [ ] Verify the UI behaves correctly when the API fails

### Success criteria
- The board remains available across refreshes or app restarts for the signed-in user
- The frontend and backend behave as a single coherent product

---

## Part 8: AI connectivity

### Goal
Add a working OpenRouter-based backend integration for AI requests.

### Checklist
- [ ] Add the OpenRouter client configuration and environment handling
- [ ] Verify the backend can make a simple AI request such as a 2 + 2 test
- [ ] Keep the initial AI integration isolated and easy to test

### Tests
- [ ] Verify a simple request succeeds with the configured model and API key
- [ ] Verify errors are surfaced clearly when the API key or network path is misconfigured

### Success criteria
- The backend can successfully call the configured AI model through OpenRouter
- The implementation is ready for board-aware prompts

---

## Part 9: Structured board-aware AI actions

### Goal
Allow the AI to understand the current board and optionally propose changes to it.

### Checklist
- [ ] Send the current board JSON plus the user question and any conversation history to the AI
- [ ] Require the AI response to use a structured output schema with a text reply and optional board updates
- [ ] Validate and apply safe board updates from the AI response
- [ ] Add thorough tests for normal and edge-case AI responses

### Tests
- [ ] Verify a simple prompt returns a structured response
- [ ] Verify valid board updates are applied correctly
- [ ] Verify invalid or malformed AI output is handled safely

### Success criteria
- The AI can answer user requests while optionally modifying the board
- The backend rejects malformed AI output without corrupting board state

---

## Part 10: AI chat sidebar experience

### Goal
Provide a polished UI for chatting with the AI and let AI-driven updates refresh the board automatically.

### Checklist
- [ ] Add a sidebar chat panel to the app shell
- [ ] Send user prompts to the backend and show the AI responses in the UI
- [ ] Apply AI-generated board updates and refresh the board automatically
- [ ] Keep the experience simple and visually aligned with the existing design system

### Tests
- [ ] Verify chat messages render correctly
- [ ] Verify AI-driven board updates are reflected in the UI
- [ ] Verify the app remains usable when the AI response contains no board changes

### Success criteria
- The user can chat with the AI from the app and see board updates when appropriate
- The experience feels cohesive with the current Kanban UI