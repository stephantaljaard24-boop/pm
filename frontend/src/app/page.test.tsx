import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Home from "@/app/page";

describe("Home page auth gate", () => {
  it("shows the login form before authentication", () => {
    render(<Home />);

    expect(screen.getByRole("heading", { name: /sign in to continue/i })).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/user/i)).toBeInTheDocument();
  });

  it("allows a user to sign in and log out", async () => {
    render(<Home />);

    await userEvent.type(screen.getByPlaceholderText(/user/i), "user");
    await userEvent.type(screen.getByPlaceholderText(/password/i), "password");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(screen.getByText(/single board kanban/i)).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /log out/i }));

    expect(screen.getByRole("heading", { name: /sign in to continue/i })).toBeInTheDocument();
  });

  it("shows an error for invalid credentials", async () => {
    render(<Home />);

    await userEvent.type(screen.getByPlaceholderText(/user/i), "wrong");
    await userEvent.type(screen.getByPlaceholderText(/password/i), "pass");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(screen.getByText(/credentials you entered are not valid/i)).toBeInTheDocument();
  });
});
