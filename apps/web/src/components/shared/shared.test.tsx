import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Inbox } from "lucide-react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { CalibratingBadge } from "@/components/shared/CalibratingBadge";
import { ComingSoon } from "@/components/shared/ComingSoon";
import { EmptyState } from "@/components/shared/EmptyState";
import { ErrorState } from "@/components/shared/ErrorState";
import { LoadingSkeleton } from "@/components/shared/LoadingSkeleton";
import { ProgressBar } from "@/components/shared/ProgressBar";
import { ScoreRing } from "@/components/shared/ScoreRing";
import { StatCard } from "@/components/shared/StatCard";
import { UnverifiedBadge } from "@/components/shared/UnverifiedBadge";
import { ApiError } from "@/lib/api/errors";

describe("ScoreRing", () => {
  it("shows no number when the value is null (never a fake score)", () => {
    render(<ScoreRing value={null} label="CodeMind Score" />);
    expect(screen.getByText("Not measured")).toBeInTheDocument();
    expect(screen.getByLabelText("CodeMind Score: not measured yet")).toBeInTheDocument();
    expect(screen.queryByText(/^\d+$/)).not.toBeInTheDocument();
  });

  it("shows the value when measured", () => {
    render(<ScoreRing value={72.4} label="DSA" />);
    expect(screen.getByText("72")).toBeInTheDocument();
    expect(screen.getByLabelText("DSA: 72 out of 100")).toBeInTheDocument();
  });
});

describe("ProgressBar", () => {
  it("exposes accessible progress semantics and clamps", () => {
    render(<ProgressBar value={150} label="Profile completeness" />);
    const bar = screen.getByRole("progressbar", { name: "Profile completeness" });
    expect(bar).toHaveAttribute("aria-valuenow", "100");
    expect(screen.getByText("100%")).toBeInTheDocument();
  });
});

describe("StatCard", () => {
  it("renders 'Not measured yet' for null", () => {
    render(<StatCard label="Readiness" value={null} />);
    expect(screen.getByText("Not measured yet")).toBeInTheDocument();
  });
  it("renders a provided value", () => {
    render(<StatCard label="Streak" value={4} hint="days" />);
    expect(screen.getByText("4")).toBeInTheDocument();
  });
});

describe("badges", () => {
  it("CalibratingBadge says calibrating and carries no score", () => {
    render(<CalibratingBadge detail="3 of 8" />);
    expect(screen.getByText(/Calibrating · 3 of 8/)).toBeInTheDocument();
  });
  it("UnverifiedBadge explains that it does not affect scores", () => {
    render(<UnverifiedBadge />);
    expect(screen.getByText("Unverified")).toHaveAttribute(
      "title",
      expect.stringContaining("does not affect"),
    );
  });
});

describe("states", () => {
  it("LoadingSkeleton is announced as busy", () => {
    render(<LoadingSkeleton label="Loading missions" />);
    expect(screen.getByRole("status")).toHaveAttribute("aria-busy", "true");
    expect(screen.getByText("Loading missions…")).toBeInTheDocument();
  });

  it("EmptyState renders title, description and action", () => {
    render(
      <EmptyState
        icon={Inbox}
        title="Nothing here"
        description="Add something"
        action={<button>Add</button>}
      />,
    );
    expect(screen.getByRole("heading", { name: "Nothing here" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Add" })).toBeInTheDocument();
  });

  it("ErrorState is an alert, shows the request id and retries", async () => {
    const onRetry = vi.fn();
    const error = new ApiError({
      status: 500,
      code: "internal_error",
      message: "Server broke",
      requestId: "abc123",
    });
    render(<ErrorState error={error} onRetry={onRetry} />);
    expect(screen.getByRole("alert")).toBeInTheDocument();
    expect(screen.getByText("Server broke")).toBeInTheDocument();
    expect(screen.getByText("Reference: abc123")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Try again" }));
    expect(onRetry).toHaveBeenCalledOnce();
  });

  it("ComingSoon says so and shows no figures", () => {
    render(
      <MemoryRouter>
        <ComingSoon
          eyebrow="Plan"
          title="Roadmap"
          description="desc"
          willInclude={["Thing one", "Thing two"]}
        />
      </MemoryRouter>,
    );
    expect(screen.getByRole("heading", { name: "Coming soon" })).toBeInTheDocument();
    expect(screen.getByText("Thing one")).toBeInTheDocument();
    expect(document.body.textContent).not.toMatch(/\d+%/);
  });
});
