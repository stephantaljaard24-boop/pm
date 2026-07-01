import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import { chatWithBoardAi, fetchBoard, saveBoard } from "@/lib/api";
import { initialData } from "@/lib/kanban";
import { KanbanBoard } from "@/components/KanbanBoard";

vi.mock("@/lib/api", () => ({
  chatWithBoardAi: vi.fn(),
  fetchBoard: vi.fn(),
  saveBoard: vi.fn(),
}));

const mockedFetchBoard = vi.mocked(fetchBoard);
const mockedSaveBoard = vi.mocked(saveBoard);
const mockedChatWithBoardAi = vi.mocked(chatWithBoardAi);

const getFirstColumn = async () => {
  const column = await screen.findAllByTestId(/column-/i);
  return column[0];
};

describe("KanbanBoard", () => {
  beforeEach(() => {
    mockedFetchBoard.mockResolvedValue(initialData);
    mockedSaveBoard.mockImplementation(async (_userId, board) => board);
    mockedChatWithBoardAi.mockReset();
  });

  it("renders five columns", async () => {
    render(<KanbanBoard />);
    expect(await screen.findAllByTestId(/column-/i)).toHaveLength(5);
  });

  it("renames a column", async () => {
    render(<KanbanBoard />);
    const column = await getFirstColumn();
    const input = within(column).getByLabelText("Column title");
    await userEvent.clear(input);
    await userEvent.type(input, "New Name");
    expect(input).toHaveValue("New Name");
  });

  it("adds and removes a card", async () => {
    render(<KanbanBoard />);
    const column = await getFirstColumn();
    const addButton = within(column).getByRole("button", {
      name: /add a card/i,
    });
    await userEvent.click(addButton);

    const titleInput = within(column).getByPlaceholderText(/card title/i);
    await userEvent.type(titleInput, "New card");
    const detailsInput = within(column).getByPlaceholderText(/details/i);
    await userEvent.type(detailsInput, "Notes");

    await userEvent.click(within(column).getByRole("button", { name: /add card/i }));

    expect(within(column).getByText("New card")).toBeInTheDocument();

    const deleteButton = within(column).getByRole("button", {
      name: /delete new card/i,
    });
    await userEvent.click(deleteButton);

    expect(within(column).queryByText("New card")).not.toBeInTheDocument();
  });

  it("shows an AI response without changing the board", async () => {
    mockedChatWithBoardAi.mockResolvedValue({
      reply: "The board has five columns.",
      board: null,
    });
    render(<KanbanBoard />);

    await userEvent.type(
      screen.getByPlaceholderText(/ask the ai to update the board/i),
      "Summarize this board"
    );
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    expect(await screen.findByText("Summarize this board")).toBeInTheDocument();
    expect(await screen.findByText("The board has five columns.")).toBeInTheDocument();
  });

  it("applies AI board updates", async () => {
    mockedChatWithBoardAi.mockResolvedValue({
      reply: "Added the card.",
      board: {
        columns: [
          {
            ...initialData.columns[0],
            cardIds: [...initialData.columns[0].cardIds, "card-ai"],
          },
          ...initialData.columns.slice(1),
        ],
        cards: {
          ...initialData.cards,
          "card-ai": {
            id: "card-ai",
            title: "AI created card",
            details: "Created from chat.",
          },
        },
      },
    });
    render(<KanbanBoard />);

    await userEvent.type(
      screen.getByPlaceholderText(/ask the ai to update the board/i),
      "Create a card"
    );
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    await waitFor(() => {
      expect(screen.getByText("AI created card")).toBeInTheDocument();
    });
    expect(screen.getByText("Added the card.")).toBeInTheDocument();
  });

  it("shows an AI error when the request fails", async () => {
    const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {});
    mockedChatWithBoardAi.mockRejectedValue(new Error("AI unavailable"));
    render(<KanbanBoard />);

    await userEvent.type(
      screen.getByPlaceholderText(/ask the ai to update the board/i),
      "Create a card"
    );
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    expect(
      await screen.findByText(/the ai request failed/i)
    ).toBeInTheDocument();
    consoleErrorSpy.mockRestore();
  });
});
