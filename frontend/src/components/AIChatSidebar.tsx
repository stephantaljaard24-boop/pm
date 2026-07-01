import { useState, type FormEvent } from "react";
import type { ChatMessagePayload } from "@/lib/api";

type AIChatSidebarProps = {
  messages: ChatMessagePayload[];
  isSending: boolean;
  error: string;
  onSend: (message: string) => Promise<void>;
};

export const AIChatSidebar = ({
  messages,
  isSending,
  error,
  onSend,
}: AIChatSidebarProps) => {
  const [draftMessage, setDraftMessage] = useState("");

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const nextMessage = draftMessage.trim();
    if (!nextMessage || isSending) {
      return;
    }

    setDraftMessage("");
    await onSend(nextMessage);
  };

  return (
    <aside className="flex min-h-[520px] flex-col rounded-[24px] border border-[var(--stroke)] bg-[var(--navy-dark)] p-5 text-white shadow-[var(--shadow)] lg:sticky lg:top-8 lg:max-h-[calc(100vh-4rem)]">
      <div className="border-b border-white/10 pb-4">
        <p className="text-xs font-semibold uppercase tracking-[0.25em] text-white/50">
          AI assistant
        </p>
        <h2 className="mt-2 font-display text-2xl font-semibold">
          Board pilot
        </h2>
      </div>

      <div
        className="mt-5 flex flex-1 flex-col gap-3 overflow-y-auto pr-1"
        aria-live="polite"
      >
        {messages.length === 0 ? (
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm leading-6 text-white/70">
            Ask for a summary, a new card, or a move across columns.
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={
                message.role === "user"
                  ? "ml-6 rounded-2xl bg-[var(--primary-blue)] px-4 py-3 text-sm leading-6 text-white"
                  : "mr-6 rounded-2xl border border-white/10 bg-white/[0.08] px-4 py-3 text-sm leading-6 text-white/80"
              }
            >
              {message.content}
            </div>
          ))
        )}
      </div>

      {error ? (
        <p className="mt-4 rounded-xl border border-red-300/40 bg-red-500/15 px-3 py-2 text-sm text-red-50">
          {error}
        </p>
      ) : null}

      <form onSubmit={handleSubmit} className="mt-4 space-y-3">
        <textarea
          value={draftMessage}
          onChange={(event) => setDraftMessage(event.target.value)}
          placeholder="Ask the AI to update the board"
          rows={4}
          className="w-full resize-none rounded-2xl border border-white/10 bg-white px-4 py-3 text-sm leading-6 text-[var(--navy-dark)] outline-none transition focus:border-[var(--accent-yellow)]"
        />
        <button
          type="submit"
          disabled={isSending || !draftMessage.trim()}
          className="w-full rounded-full bg-[var(--secondary-purple)] px-4 py-3 text-sm font-semibold uppercase tracking-[0.16em] text-white transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isSending ? "Sending" : "Send"}
        </button>
      </form>
    </aside>
  );
};
