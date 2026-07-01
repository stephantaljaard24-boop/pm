"use client";

import { useState, type FormEvent } from "react";

type LoginFormProps = {
  onSubmit: (username: string, password: string) => void;
  error?: string;
};

export const LoginForm = ({ onSubmit, error }: LoginFormProps) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSubmit(username.trim(), password);
  };

  return (
    <form onSubmit={handleSubmit} className="mx-auto flex w-full max-w-md flex-col gap-4 rounded-[32px] border border-[var(--stroke)] bg-white/90 p-8 shadow-[var(--shadow)]">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
          Project Management MVP
        </p>
        <h1 className="mt-3 font-display text-3xl font-semibold text-[var(--navy-dark)]">
          Sign in to continue
        </h1>
        <p className="mt-3 text-sm leading-6 text-[var(--gray-text)]">
          Use the demo credentials user / password to access the Kanban board.
        </p>
      </div>

      {error ? (
        <p className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </p>
      ) : null}

      <label className="flex flex-col gap-2 text-sm font-medium text-[var(--navy-dark)]">
        Username
        <input
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          className="rounded-2xl border border-[var(--stroke)] bg-[var(--surface)] px-4 py-3 outline-none transition focus:border-[var(--primary-blue)]"
          placeholder="user"
          autoComplete="username"
        />
      </label>

      <label className="flex flex-col gap-2 text-sm font-medium text-[var(--navy-dark)]">
        Password
        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          className="rounded-2xl border border-[var(--stroke)] bg-[var(--surface)] px-4 py-3 outline-none transition focus:border-[var(--primary-blue)]"
          placeholder="password"
          autoComplete="current-password"
        />
      </label>

      <button
        type="submit"
        className="rounded-full bg-[var(--secondary-purple)] px-4 py-3 text-sm font-semibold uppercase tracking-[0.2em] text-white transition hover:brightness-110"
      >
        Sign in
      </button>
    </form>
  );
};
