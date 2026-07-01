# Frontend guidance

## Current state

The frontend is a Next.js static app served by the FastAPI backend in production. The main page gates access behind the MVP sign-in form, then renders the Kanban workspace with draggable cards, editable column names, add/remove card actions, and an AI chat sidebar.

## Key structure

- [src/app/page.tsx](src/app/page.tsx): MVP auth gate and app shell.
- [src/components/KanbanBoard.tsx](src/components/KanbanBoard.tsx): top-level board state, drag-and-drop handlers, persistence calls, and AI sidebar integration.
- [src/components/AIChatSidebar.tsx](src/components/AIChatSidebar.tsx): chat message list, prompt form, loading state, and error display.
- [src/components/KanbanColumn.tsx](src/components/KanbanColumn.tsx): renders each column, handles dropping cards, and includes the add-card form.
- [src/components/KanbanCard.tsx](src/components/KanbanCard.tsx): renders an individual card and supports drag behavior.
- [src/components/NewCardForm.tsx](src/components/NewCardForm.tsx): compact form for creating a new card.
- [src/lib/api.ts](src/lib/api.ts): frontend API wrappers for board persistence and AI chat.
- [src/lib/kanban.ts](src/lib/kanban.ts): shared board data types, initial board data, and the card movement logic.
- [src/components/KanbanBoard.test.tsx](src/components/KanbanBoard.test.tsx): component tests for rendering, board actions, AI responses, AI updates, and AI errors.
- [src/lib/kanban.test.ts](src/lib/kanban.test.ts): unit tests for the drag-and-drop movement logic.

## Current behavior

- The board renders immediately from seeded data, then loads persisted data from the backend.
- Columns are editable directly in the UI.
- Cards can be moved between columns using drag and drop.
- New cards can be created within a column.
- Existing cards can be deleted from a column.
- Board changes are persisted through the backend API.
- The AI sidebar sends prompts to the backend and can replace the local board with a validated AI-generated update.

## Tooling and commands

Run the frontend locally with:

- npm install
- npm run dev

Run the current test suite with:

- npm run test:unit

Run the browser-based tests with:

- npm run test:e2e

Create the static production build with:

- npm run build

## Implementation notes for future work

- Keep the existing design system and visual language intact when adding new UI features.
- Preserve the current component boundaries where possible; board state currently lives in the board component, while shared Kanban logic remains in the library module.
- Keep UI logic separated from the API layer. Add API wrappers in `src/lib/api.ts` rather than calling fetch directly from many components.
- AI-generated board updates should flow through the same `BoardData` shape used by the board.
- Prefer small, testable changes and add or update tests alongside production changes.
