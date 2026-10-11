import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { ForgotPasswordPage } from "@/features/auth/ForgotPasswordPage";
import { LoginPage } from "@/features/auth/LoginPage";
import { RegisterPage } from "@/features/auth/RegisterPage";
import { renderWithProviders } from "@/test/render";

const inRouter = (ui: React.ReactElement) => <MemoryRouter>{ui}</MemoryRouter>;

describe("LoginPage", () => {
  it("validates before calling Firebase", async () => {
    const signInWithEmail = vi.fn();
    renderWithProviders(inRouter(<LoginPage />), { signInWithEmail });
    await userEvent.click(screen.getByRole("button", { name: "Sign in" }));
    expect(await screen.findByText("Enter your email.")).toBeInTheDocument();
    expect(screen.getByText("Enter your password.")).toBeInTheDocument();
    expect(signInWithEmail).not.toHaveBeenCalled();
  });

  it("signs in with the entered credentials", async () => {
    const signInWithEmail = vi.fn().mockResolvedValue(undefined);
    renderWithProviders(inRouter(<LoginPage />), { signInWithEmail });
    await userEvent.type(screen.getByLabelText("Email"), "asha@example.com");
    await userEvent.type(screen.getByLabelText("Password"), "correct horse");
    await userEvent.click(screen.getByRole("button", { name: "Sign in" }));
    await waitFor(() =>
      expect(signInWithEmail).toHaveBeenCalledWith("asha@example.com", "correct horse"),
    );
  });

  it("shows a friendly message for wrong credentials without leaking the Firebase code", async () => {
    const signInWithEmail = vi.fn().mockRejectedValue({ code: "auth/invalid-credential" });
    renderWithProviders(inRouter(<LoginPage />), { signInWithEmail });
    await userEvent.type(screen.getByLabelText("Email"), "a@b.co");
    await userEvent.type(screen.getByLabelText("Password"), "x");
    await userEvent.click(screen.getByRole("button", { name: "Sign in" }));
    expect(await screen.findByText("Incorrect email or password.")).toBeInTheDocument();
    expect(screen.queryByText(/auth\//)).not.toBeInTheDocument();
  });

  it("explains when Firebase is not configured and disables sign-in", () => {
    renderWithProviders(inRouter(<LoginPage />), { firebaseConfigured: false });
    expect(screen.getByRole("alert")).toHaveTextContent("Firebase is not configured");
    expect(screen.getByRole("button", { name: "Sign in" })).toBeDisabled();
    expect(screen.getByRole("button", { name: /Continue with Google/ })).toBeDisabled();
  });
});

describe("RegisterPage", () => {
  it("rejects short and mismatched passwords", async () => {
    const registerWithEmail = vi.fn();
    renderWithProviders(inRouter(<RegisterPage />), { registerWithEmail });
    await userEvent.type(screen.getByLabelText("Email"), "a@b.co");
    await userEvent.type(screen.getByLabelText("Password"), "short");
    await userEvent.type(screen.getByLabelText("Confirm password"), "different");
    await userEvent.click(screen.getByRole("button", { name: "Create account" }));
    expect(await screen.findByText("Use at least 8 characters.")).toBeInTheDocument();
    expect(registerWithEmail).not.toHaveBeenCalled();
  });

  it("registers with a valid form", async () => {
    const registerWithEmail = vi.fn().mockResolvedValue(undefined);
    renderWithProviders(inRouter(<RegisterPage />), { registerWithEmail });
    await userEvent.type(screen.getByLabelText("Email"), "new@example.com");
    await userEvent.type(screen.getByLabelText("Password"), "longenough1");
    await userEvent.type(screen.getByLabelText("Confirm password"), "longenough1");
    await userEvent.click(screen.getByRole("button", { name: "Create account" }));
    await waitFor(() =>
      expect(registerWithEmail).toHaveBeenCalledWith("new@example.com", "longenough1"),
    );
  });

  it("reports an existing account clearly", async () => {
    const registerWithEmail = vi.fn().mockRejectedValue({ code: "auth/email-already-in-use" });
    renderWithProviders(inRouter(<RegisterPage />), { registerWithEmail });
    await userEvent.type(screen.getByLabelText("Email"), "dup@example.com");
    await userEvent.type(screen.getByLabelText("Password"), "longenough1");
    await userEvent.type(screen.getByLabelText("Confirm password"), "longenough1");
    await userEvent.click(screen.getByRole("button", { name: "Create account" }));
    expect(await screen.findByText(/already exists/)).toBeInTheDocument();
  });
});

describe("ForgotPasswordPage", () => {
  it("shows the same neutral confirmation whether or not the account exists", async () => {
    const sendPasswordReset = vi.fn().mockRejectedValue({ code: "auth/user-not-found" });
    renderWithProviders(inRouter(<ForgotPasswordPage />), { sendPasswordReset });
    await userEvent.type(screen.getByLabelText("Email"), "ghost@example.com");
    await userEvent.click(screen.getByRole("button", { name: "Send reset link" }));
    expect(await screen.findByRole("status")).toHaveTextContent("If an account exists");
  });
});
