import type { ProfileIn, ProfileOut } from "@codemind/shared";
import { z } from "zod";

/**
 * Client-side validation. It mirrors the backend's Pydantic rules (apps/api/app/schemas/profile.py)
 * so students get instant feedback. The server remains the source of truth and its field errors
 * are shown too.
 */
const GITHUB = /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$/;
const LEETCODE = /^[A-Za-z0-9_-]{1,40}$/;
const CODEFORCES = /^[A-Za-z0-9_.-]{3,24}$/;
// \p{L}\p{N}_ mirrors Python's Unicode-aware \w (JavaScript's \w is ASCII-only).
const LINKEDIN = /^https:\/\/([a-z]{2,3}\.)?linkedin\.com\/in\/[\p{L}\p{N}_\-%]{3,100}\/?$/iu;
export const SKILL_PATTERN = /^[\p{L}\p{N}_][\p{L}\p{N}_ +#.\-/()]*$/u;

export const LANGUAGES = [
  { value: "python", label: "Python" },
  { value: "java", label: "Java" },
  { value: "cpp", label: "C++" },
] as const;

export const CGPA_SCALES = ["4", "5", "10"] as const;

export function supportedTimeZones(): string[] {
  const intl = Intl as unknown as { supportedValuesOf?: (key: string) => string[] };
  const zones = intl.supportedValuesOf?.("timeZone") ?? [];
  return zones.includes("UTC") ? zones : ["UTC", ...zones];
}

export function defaultTimeZone(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
  } catch {
    return "UTC";
  }
}

const text120 = z.string().trim().max(120, "Keep this under 120 characters.");
const blankOr = (pattern: RegExp, message: string) =>
  z
    .string()
    .trim()
    .refine((value) => value === "" || pattern.test(value), message);

export const profileSchema = z
  .object({
    name: z
      .string()
      .trim()
      .min(1, "Enter your name.")
      .max(100, "Keep your name under 100 characters."),
    college: text120,
    degree: text120,
    current_year: z.string().regex(/^[1-8]?$/, "Choose a year between 1 and 8."),
    cgpa: blankOr(/^\d{1,2}(\.\d{1,2})?$/, "Use up to two decimals, for example 8.75."),
    cgpa_scale: z.enum(CGPA_SCALES),
    skills: z
      .array(
        z
          .string()
          .trim()
          .min(1)
          .max(40, "A skill can be at most 40 characters.")
          .regex(SKILL_PATTERN, "Use letters, digits or + # . - / ( ) in skills."),
      )
      .max(30, "Add at most 30 skills."),
    dream_company: text120,
    dream_role: text120,
    target_package_lpa: blankOr(
      /^\d{1,4}(\.\d{1,2})?$/,
      "Enter a number such as 24 or 24.5 (LPA).",
    ),
    github_username: blankOr(GITHUB, "Enter your GitHub username, not a URL."),
    linkedin_url: blankOr(LINKEDIN, "Use a profile URL like https://linkedin.com/in/your-name."),
    leetcode_username: blankOr(LEETCODE, "Letters, digits, '_' and '-' only."),
    codeforces_username: blankOr(CODEFORCES, "3-24 characters: letters, digits, '_', '-' or '.'."),
    timezone: z.string().min(1, "Choose your time zone."),
    daily_minutes: z
      .string()
      .trim()
      .refine(
        (value) =>
          value === "" || (/^\d+$/.test(value) && Number(value) >= 15 && Number(value) <= 720),
        "Enter a whole number of minutes between 15 and 720.",
      ),
    preferred_language: z.enum(["", "python", "java", "cpp"]),
  })
  .superRefine((values, ctx) => {
    if (values.cgpa !== "" && Number(values.cgpa) > Number(values.cgpa_scale)) {
      ctx.addIssue({
        code: "custom",
        path: ["cgpa"],
        message: `Your CGPA cannot be higher than the scale (${values.cgpa_scale}).`,
      });
    }
  });

export type ProfileFormValues = z.infer<typeof profileSchema>;

export function emptyProfileValues(): ProfileFormValues {
  return {
    name: "",
    college: "",
    degree: "",
    current_year: "",
    cgpa: "",
    cgpa_scale: "10",
    skills: [],
    dream_company: "",
    dream_role: "",
    target_package_lpa: "",
    github_username: "",
    linkedin_url: "",
    leetcode_username: "",
    codeforces_username: "",
    timezone: defaultTimeZone(),
    daily_minutes: "",
    preferred_language: "",
  };
}

const orEmpty = (value: string | number | null | undefined): string =>
  value === null || value === undefined ? "" : String(value);

export function toFormValues(profile: ProfileOut): ProfileFormValues {
  const scale = String(profile.cgpa_scale);
  return {
    name: profile.name,
    college: orEmpty(profile.college),
    degree: orEmpty(profile.degree),
    current_year: orEmpty(profile.current_year),
    cgpa: orEmpty(profile.cgpa),
    cgpa_scale: (CGPA_SCALES as readonly string[]).includes(scale)
      ? (scale as ProfileFormValues["cgpa_scale"])
      : "10",
    skills: profile.skills,
    dream_company: orEmpty(profile.dream_company),
    dream_role: orEmpty(profile.dream_role),
    target_package_lpa: orEmpty(profile.target_package_lpa),
    github_username: orEmpty(profile.github_username),
    linkedin_url: orEmpty(profile.linkedin_url),
    leetcode_username: orEmpty(profile.leetcode_username),
    codeforces_username: orEmpty(profile.codeforces_username),
    timezone: profile.timezone,
    daily_minutes: orEmpty(profile.daily_minutes),
    preferred_language: (["python", "java", "cpp"].includes(profile.preferred_language ?? "")
      ? profile.preferred_language
      : "") as ProfileFormValues["preferred_language"],
  };
}

const nullIfBlank = (value: string): string | null => (value.trim() === "" ? null : value.trim());
const numberOrNull = (value: string): number | null => (value.trim() === "" ? null : Number(value));

export function toProfileIn(values: ProfileFormValues): ProfileIn {
  return {
    name: values.name.trim(),
    college: nullIfBlank(values.college),
    degree: nullIfBlank(values.degree),
    current_year: numberOrNull(values.current_year),
    cgpa: numberOrNull(values.cgpa),
    cgpa_scale: Number(values.cgpa_scale) as 4 | 5 | 10,
    skills: values.skills,
    dream_company: nullIfBlank(values.dream_company),
    dream_role: nullIfBlank(values.dream_role),
    target_package_lpa: numberOrNull(values.target_package_lpa),
    github_username: nullIfBlank(values.github_username),
    linkedin_url: nullIfBlank(values.linkedin_url),
    leetcode_username: nullIfBlank(values.leetcode_username),
    codeforces_username: nullIfBlank(values.codeforces_username),
    timezone: values.timezone,
    daily_minutes: numberOrNull(values.daily_minutes),
    preferred_language: values.preferred_language === "" ? null : values.preferred_language,
  };
}
