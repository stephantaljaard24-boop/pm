"use client";

import { useMemo, useState } from "react";
import { KanbanBoard } from "@/components/KanbanBoard";
import { LoginForm } from "@/components/LoginForm";

const DEMO_USERNAME = "user";
const DEMO_PASSWORD = "password";

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authError, setAuthError] = useState("");

  const handleLogin = (username: string, password: string) => {
    if (username === DEMO_USERNAME && password === DEMO_PASSWORD) {
      setIsAuthenticated(true);
      setAuthError("");
      return;
    }

    setIsAuthenticated(false);
    setAuthError("The credentials you entered are not valid.");
  };

  const authState = useMemo(
    () => ({ isAuthenticated, authError }),
    [isAuthenticated, authError]
  );

  if (!authState.isAuthenticated) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[var(--surface)] px-6 py-16">
        <LoginForm onSubmit={handleLogin} error={authState.authError} />
      </main>
    );
  }

  return (
    <div className="relative">
      <div className="absolute right-6 top-6 z-10">
        <button
          type="button"
          onClick={() => {
            setIsAuthenticated(false);
            setAuthError("");
          }}
          className="rounded-full border border-[var(--stroke)] bg-white/80 px-4 py-2 text-sm font-semibold uppercase tracking-[0.2em] text-[var(--navy-dark)] transition hover:border-[var(--primary-blue)]"
        >
          Log out
        </button>
      </div>
      <KanbanBoard />
    </div>
  );
}
