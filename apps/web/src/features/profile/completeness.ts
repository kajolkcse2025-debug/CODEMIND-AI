import type { ProfileOut } from "@codemind/shared";

export interface Completeness {
  filled: number;
  total: number;
  percent: number;
  missing: string[];
}

/** How much of the profile is filled in. A real count of real fields, not a skill score. */
export function profileCompleteness(profile: ProfileOut): Completeness {
  const checks: [string, boolean][] = [
    ["College", Boolean(profile.college)],
    ["Degree", Boolean(profile.degree)],
    ["Year of study", profile.current_year !== null],
    ["CGPA", profile.cgpa !== null],
    ["Skills", profile.skills.length > 0],
    ["Dream company", Boolean(profile.dream_company)],
    ["Dream role", Boolean(profile.dream_role)],
    ["Daily study time", profile.daily_minutes !== null],
    ["Preferred language", Boolean(profile.preferred_language)],
  ];
  const filled = checks.filter(([, ok]) => ok).length;
  return {
    filled,
    total: checks.length,
    percent: Math.round((filled / checks.length) * 100),
    missing: checks.filter(([, ok]) => !ok).map(([label]) => label),
  };
}
