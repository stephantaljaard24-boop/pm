export type BoardPayload = {
  columns: Array<{ id: string; title: string; cardIds: string[] }>;
  cards: Record<string, { id: string; title: string; details: string }>;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const fetchBoard = async (userId: string): Promise<BoardPayload> => {
  const response = await fetch(`${API_BASE_URL}/api/board/${userId}`);
  if (!response.ok) {
    throw new Error("Failed to load board");
  }
  return response.json();
};

export const saveBoard = async (userId: string, board: BoardPayload): Promise<BoardPayload> => {
  const response = await fetch(`${API_BASE_URL}/api/board/${userId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(board),
  });

  if (!response.ok) {
    throw new Error("Failed to save board");
  }

  return response.json();
};
