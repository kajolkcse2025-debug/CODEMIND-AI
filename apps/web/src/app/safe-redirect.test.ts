import { describe, expect, it } from "vitest";

import { safeRedirectPath } from "@/app/safe-redirect";

describe("safeRedirectPath", () => {
  it.each(["/dashboard", "/profile?tab=goals", "/settings#appearance", "/"])(
    "allows %s",
    (path) => {
      expect(safeRedirectPath(path)).toBe(path);
    },
  );

  it.each([
    ["protocol-relative", "//evil.example"],
    ["backslash variant", "/\\evil.example"],
    ["tab smuggling", "/\t/evil.example"],
    ["newline smuggling", "/\n/evil.example"],
    ["absolute URL", "https://evil.example"],
    ["javascript URL", "javascript:alert(1)"],
    ["relative path", "dashboard"],
    ["empty", ""],
    ["undefined", undefined],
    ["non-string", { a: 1 }],
    ["space inside", "/a b"],
  ])("rejects %s", (_label, candidate) => {
    expect(safeRedirectPath(candidate)).toBe("/dashboard");
  });

  it("uses the supplied fallback", () => {
    expect(safeRedirectPath("//x", "/home")).toBe("/home");
  });
});
