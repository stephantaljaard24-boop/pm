# Kanban Studio

Next.js frontend for the Project Management MVP. In production it is exported as a static site and served by the FastAPI backend.

## What It Includes

- MVP sign-in screen.
- Persistent Kanban board UI.
- Editable column names.
- Card creation, deletion, and drag-and-drop movement.
- AI chat sidebar that can request board updates from the backend.

## Run Frontend Only

```bash
npm install
npm run dev
```

The standalone dev server is useful for UI work. Full persistence and AI behavior require the backend API.

## Tests

```bash
npm run test:unit
npm run test:e2e
npm run build
```

## Integration

The API base URL defaults to `http://localhost:8000`. Override it with:

```text
NEXT_PUBLIC_API_URL=http://your-backend-host
```

The production container builds this frontend with `npm run build` and copies `frontend/out` into the backend image.
