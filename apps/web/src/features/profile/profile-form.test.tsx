import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ProfileForm } from "@/features/profile/ProfileForm";
import { emptyProfileValues } from "@/features/profile/schema";
import { ApiError } from "@/lib/api/errors";
import { renderWithProviders } from "@/test/render";

const defaults = () => ({ ...emptyProfileValues(), timezone: "Asia/Kolkata" });

describe("ProfileForm", () => {
  it("requires a name and does not submit", async () => {
    const onSubmit = vi.fn();
    renderWithProviders(
      <ProfileForm defaultValues={defaults()} onSubmit={onSubmit} submitLabel="Save" />,
    );
    await userEvent.click(screen.getByRole("button", { name: "Save" }));
    expect(await screen.findByText("Enter your name.")).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("submits a typed payload (numbers as numbers, blanks as null, skills as a list)", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    const onSaved = vi.fn();
    renderWithProviders(
      <ProfileForm
        defaultValues={defaults()}
        onSubmit={onSubmit}
        onSaved={onSaved}
        submitLabel="Save"
      />,
    );
    await userEvent.type(screen.getByLabelText("Name"), "Asha Kumar");
    await userEvent.type(screen.getByLabelText(/CGPA/), "8.75");
    await userEvent.type(screen.getByLabelText(/Daily study time/), "90");
    await userEvent.type(
      screen.getByLabelText("Skills", { exact: false }),
      "Python{enter}SQL{enter}",
    );
    await userEvent.click(screen.getByRole("button", { name: "Save" }));
    await waitFor(() => expect(onSubmit).toHaveBeenCalledOnce());
    const payload = onSubmit.mock.calls[0]![0];
    expect(payload).toMatchObject({
      name: "Asha Kumar",
      cgpa: 8.75,
      daily_minutes: 90,
      college: null,
      skills: ["Python", "SQL"],
      timezone: "Asia/Kolkata",
    });
    expect(payload).not.toHaveProperty("user_id");
    expect(onSaved).toHaveBeenCalled();
  });

  it("blocks a CGPA higher than the selected scale", async () => {
    const onSubmit = vi.fn();
    renderWithProviders(
      <ProfileForm defaultValues={defaults()} onSubmit={onSubmit} submitLabel="Save" />,
    );
    await userEvent.type(screen.getByLabelText("Name"), "Asha");
    await userEvent.type(screen.getByLabelText(/CGPA/), "11");
    await userEvent.click(screen.getByRole("button", { name: "Save" }));
    expect(await screen.findByText(/cannot be higher than the scale/)).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("shows server-side field errors next to the right field", async () => {
    const onSubmit = vi.fn().mockRejectedValue(
      new ApiError({
        status: 422,
        code: "validation_error",
        message: "The request contains invalid data.",
        details: {
          errors: [{ field: "github_username", issue: "must be a valid GitHub username" }],
        },
      }),
    );
    renderWithProviders(
      <ProfileForm defaultValues={defaults()} onSubmit={onSubmit} submitLabel="Save" />,
    );
    await userEvent.type(screen.getByLabelText("Name"), "Asha");
    await userEvent.click(screen.getByRole("button", { name: "Save" }));
    expect(await screen.findByText("must be a valid GitHub username")).toBeInTheDocument();
    expect(screen.getByLabelText(/GitHub username/)).toHaveAttribute("aria-invalid", "true");
  });

  it("shows a general error banner for non-validation failures", async () => {
    const onSubmit = vi
      .fn()
      .mockRejectedValue(new ApiError({ status: 0, code: "network_error", message: "x" }));
    renderWithProviders(
      <ProfileForm defaultValues={defaults()} onSubmit={onSubmit} submitLabel="Save" />,
    );
    await userEvent.type(screen.getByLabelText("Name"), "Asha");
    await userEvent.click(screen.getByRole("button", { name: "Save" }));
    expect(await screen.findByText(/could not reach the server/i)).toBeInTheDocument();
  });
});
