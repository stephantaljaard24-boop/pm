# Frontend guidance

## Current state

The frontend is a Next.js app that already contains a working demo Kanban experience. The main page renders a board with draggable cards, editable column names, and the ability to add or remove cards.

## Key structure

- [src/app/page.tsx](src/app/page.tsx): renders the Kanban board on the home route.
- [src/components/KanbanBoard.tsx](src/components/KanbanBoard.tsx): top-level board state, drag-and-drop handlers, and board-level actions.
- [src/components/KanbanColumn.tsx](src/components/KanbanColumn.tsx): renders each column, handles dropping cards, and includes the add-card form.
- [src/components/KanbanCard.tsx](src/components/KanbanCard.tsx): renders an individual card and supports drag behavior.
- [src/components/NewCardForm.tsx](src/components/NewCardForm.tsx): compact form for creating a new card.
- [src/lib/kanban.ts](src/lib/kanban.ts): shared board data types, initial board data, and the card movement logic.
- [src/components/KanbanBoard.test.tsx](src/components/KanbanBoard.test.tsx): component tests for rendering, renaming columns, and adding/removing cards.
- [src/lib/kanban.test.ts](src/lib/kanban.test.ts): unit tests for the drag-and-drop movement logic.

## Current behavior

- The board starts from a seeded in-memory dataset.
- Columns are editable directly in the UI.
- Cards can be moved between columns using drag and drop.
- New cards can be created within a column.
- Existing cards can be deleted from a column.

## Tooling and commands

Run the frontend locally with:

- npm install
- npm run dev

Run the current test suite with:

- npm run test:unit

Run the browser-based tests with:

- npm run test:e2e

## Implementation notes for future work

- Keep the existing design system and visual language intact when adding new UI features.
- Preserve the current component boundaries where possible; board state currently lives in the board component, while shared Kanban logic remains in the library module.
- When adding authentication, persistence, or AI-driven updates, keep the UI logic separated from the data layer so the board can evolve without becoming tightly coupled to the backend.
- Prefer small, testable changes and add or update tests alongside production changes.
