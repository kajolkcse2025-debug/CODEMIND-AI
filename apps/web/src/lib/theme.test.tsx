import { act, renderHook } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it } from "vitest";

import { ThemeProvider } from "@/lib/theme";
import { useTheme } from "@/lib/theme-context";

const wrapper = ({ children }: { children: ReactNode }) => (
  <ThemeProvider>{children}</ThemeProvider>
);

describe("theme", () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.classList.remove("dark");
  });

  it("defaults to dark", () => {
    const { result } = renderHook(() => useTheme(), { wrapper });
    expect(result.current.theme).toBe("dark");
    expect(document.documentElement).toHaveClass("dark");
  });

  it("switches to light, persists the choice, and removes the dark class", () => {
    const { result } = renderHook(() => useTheme(), { wrapper });
    act(() => result.current.setTheme("light"));
    expect(document.documentElement).not.toHaveClass("dark");
    expect(localStorage.getItem("codemind-theme")).toBe("light");
  });

  it("restores a saved preference", () => {
    localStorage.setItem("codemind-theme", "light");
    const { result } = renderHook(() => useTheme(), { wrapper });
    expect(result.current.theme).toBe("light");
  });
});
