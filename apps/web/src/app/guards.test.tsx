import { screen, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { MeResponse, ProfileOut } from "@codemind/shared";
import { renderRoute } from "@/test/render";

const meState = vi.hoisted(() => ({
  value: {
    isPending: false,
    isError: false,
    data: undefined as unknown,
    error: null,
    refetch: () => undefined,
  } as Record<string, unknown>,
}));

vi.mock("@/features/me/hooks", () => ({ useMe: () => meState.value }));

const profile: ProfileOut = {
  name: "Asha Kumar",
  college: null,
  degree: null,
  current_year: null,
  cgpa: null,
  cgpa_scale: 10,
  skills: [],
  dream_company: null,
  dream_role: null,
  target_package_lpa: null,
  github_username: null,
  linkedin_url: null,
  leetcode_username: null,
  codeforces_username: null,
  timezone: "UTC",
  daily_minutes: null,
  preferred_language: null,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

const me = (withProfile: boolean): MeResponse => ({
  user: {
    id: "u1",
    email: "asha@example.com",
    display_name: null,
    role: "student",
    onboarding_status: withProfile ? "complete" : "not_started",
    assessment_status: "not_started",
    xp_total: 0,
    level: 1,
    created_at: "2026-01-01T00:00:00Z",
  },
  profile: withProfile ? profile : null,
  flags: { email_verified: true },
});

const signedIn = { status: "authenticated" as const };

beforeEach(() => {
  meState.value = {
    isPending: false,
    isError: false,
    data: me(true),
    error: null,
    refetch: () => undefined,
  };
});

describe("route guards", () => {
  it("sends signed-out visitors from a protected page to /login", async () => {
    const { router } = renderRoute("/dashboard", { status: "unauthenticated" });
    expect(await screen.findByRole("heading", { name: "Sign in" })).toBeInTheDocument();
    expect(router.state.location.pathname).toBe("/login");
  });

  it("shows a loading state while the session is being checked", () => {
    renderRoute("/dashboard", { status: "loading" });
    expect(screen.getByRole("status")).toHaveAttribute("aria-busy", "true");
  });

  it("redirects signed-in students away from /login", async () => {
    const { router } = renderRoute("/login", signedIn);
    expect(await screen.findByRole("heading", { name: /Welcome, Asha/ })).toBeInTheDocument();
    expect(router.state.location.pathname).toBe("/dashboard");
  });

  it("sends signed-in students without a profile to onboarding", async () => {
    meState.value = { ...meState.value, data: me(false) };
    const { router } = renderRoute("/dashboard", signedIn);
    expect(await screen.findByRole("heading", { name: "Set up your profile" })).toBeInTheDocument();
    expect(router.state.location.pathname).toBe("/onboarding");
  });

  it("keeps students who already have a profile out of onboarding", async () => {
    const { router } = renderRoute("/onboarding", signedIn);
    expect(await screen.findByRole("heading", { name: /Welcome, Asha/ })).toBeInTheDocument();
    expect(router.state.location.pathname).toBe("/dashboard");
  });

  it("shows an error state with retry when the account cannot be loaded", async () => {
    meState.value = {
      isPending: false,
      isError: true,
      data: undefined,
      error: new Error("x"),
      refetch: () => undefined,
    };
    renderRoute("/dashboard", signedIn);
    expect(await screen.findByRole("alert")).toHaveTextContent("Could not load your account");
    expect(screen.getByRole("button", { name: "Try again" })).toBeInTheDocument();
  });

  it("renders the 404 page for unknown routes", async () => {
    renderRoute("/definitely-not-a-page", { status: "unauthenticated" });
    expect(await screen.findByRole("heading", { name: "Page not found" })).toBeInTheDocument();
  });
});

describe("unbuilt modules", () => {
  it.each([
    ["/assessment", "Assessment"],
    ["/coding-coach", "Coding coach"],
    ["/roadmap", "Roadmap"],
    ["/missions", "Missions"],
    ["/analytics", "Analytics"],
    ["/coding-dna", "Coding DNA"],
    ["/interview", "Interview"],
  ])("%s shows Coming soon and no figures", async (path, title) => {
    renderRoute(path, signedIn);
    expect(await screen.findByRole("heading", { level: 1, name: title })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Coming soon" })).toBeInTheDocument();
    expect(document.querySelector("main")?.textContent).not.toMatch(/\d+\s?%|\b\d{2,}\b/);
  });
});

describe("dashboard honesty", () => {
  it("shows no scores, only real setup state", async () => {
    renderRoute("/dashboard", signedIn);
    expect(await screen.findByRole("heading", { name: "Today's mission" })).toBeInTheDocument();
    expect(screen.getByText("No mission yet")).toBeInTheDocument();
    const main = within(document.querySelector("main")!);
    expect(
      main.queryByText(/CodeMind Score|Readiness|Coding DNA|Mastery/i),
    ).not.toBeInTheDocument();
    expect(main.queryByRole("progressbar", { name: /score|readiness/i })).not.toBeInTheDocument();
    expect(screen.getByText("Not available yet")).toBeInTheDocument();
  });
});
