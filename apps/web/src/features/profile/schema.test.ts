import type { ProfileOut } from "@codemind/shared";
import { describe, expect, it } from "vitest";

import { profileCompleteness } from "@/features/profile/completeness";
import {
  emptyProfileValues,
  profileSchema,
  toFormValues,
  toProfileIn,
  type ProfileFormValues,
} from "@/features/profile/schema";

const valid = (overrides: Partial<ProfileFormValues> = {}): ProfileFormValues => ({
  ...emptyProfileValues(),
  name: "Asha",
  timezone: "Asia/Kolkata",
  ...overrides,
});

const issues = (values: ProfileFormValues) => {
  const result = profileSchema.safeParse(values);
  return result.success
    ? {}
    : Object.fromEntries(result.error.issues.map((i) => [i.path.join("."), i.message]));
};

describe("profile schema", () => {
  it("accepts the minimal profile", () => {
    expect(profileSchema.safeParse(valid()).success).toBe(true);
  });

  it("requires a name", () => {
    expect(issues(valid({ name: "   " }))).toHaveProperty("name");
  });

  it.each([
    ["cgpa", "8.755"],
    ["cgpa", "abc"],
    ["target_package_lpa", "-3"],
    ["github_username", "https://github.com/x"],
    ["linkedin_url", "http://linkedin.com/in/asha"],
    ["linkedin_url", "https://evil.example/in/asha"],
    ["leetcode_username", "bad name"],
    ["codeforces_username", "ab"],
    ["daily_minutes", "5"],
    ["daily_minutes", "900"],
    ["daily_minutes", "1.5"],
  ] as const)("rejects %s = %s", (field, value) => {
    expect(issues(valid({ [field]: value }))).toHaveProperty(field);
  });

  it("rejects a CGPA above the chosen scale", () => {
    expect(issues(valid({ cgpa: "4.5", cgpa_scale: "4" }))).toHaveProperty("cgpa");
    expect(issues(valid({ cgpa: "9.2", cgpa_scale: "10" }))).toEqual({});
  });

  it("rejects bad skills", () => {
    expect(Object.keys(issues(valid({ skills: ["<script>"] }))).length).toBeGreaterThan(0);
  });
});

describe("profile payload mapping", () => {
  it("turns blanks into null and numeric strings into numbers", () => {
    const payload = toProfileIn(
      valid({
        college: "  ",
        current_year: "3",
        cgpa: "8.5",
        cgpa_scale: "10",
        daily_minutes: "90",
        preferred_language: "python",
        target_package_lpa: "",
      }),
    );
    expect(payload).toMatchObject({
      name: "Asha",
      college: null,
      current_year: 3,
      cgpa: 8.5,
      cgpa_scale: 10,
      daily_minutes: 90,
      preferred_language: "python",
      target_package_lpa: null,
    });
  });

  it("never includes a user id", () => {
    expect(Object.keys(toProfileIn(valid()))).not.toContain("user_id");
  });

  it("round-trips a server profile into form values", () => {
    const profile: ProfileOut = {
      name: "Asha",
      college: null,
      degree: "B.Tech",
      current_year: 2,
      cgpa: 8.1,
      cgpa_scale: 10,
      skills: ["Go"],
      dream_company: null,
      dream_role: null,
      target_package_lpa: null,
      github_username: null,
      linkedin_url: null,
      leetcode_username: null,
      codeforces_username: null,
      timezone: "UTC",
      daily_minutes: 60,
      preferred_language: "java",
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    };
    const values = toFormValues(profile);
    expect(values).toMatchObject({
      college: "",
      current_year: "2",
      cgpa: "8.1",
      preferred_language: "java",
    });
    expect(profileSchema.safeParse(values).success).toBe(true);
    expect(profileCompleteness(profile)).toMatchObject({ filled: 6, total: 9, percent: 67 });
  });
});
