import type { ProfileIn } from "@codemind/shared";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMemo, useState } from "react";
import { Controller, useForm, type Path } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { fieldAria } from "@/components/ui/field-aria";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { TagInput } from "@/features/profile/TagInput";
import {
  CGPA_SCALES,
  LANGUAGES,
  profileSchema,
  supportedTimeZones,
  toProfileIn,
  type ProfileFormValues,
} from "@/features/profile/schema";
import { describeError, fieldErrors } from "@/lib/api";

interface ProfileFormProps {
  defaultValues: ProfileFormValues;
  onSubmit: (payload: ProfileIn) => Promise<unknown>;
  submitLabel: string;
  onSaved?: () => void;
}

export function ProfileForm({ defaultValues, onSubmit, submitLabel, onSaved }: ProfileFormProps) {
  const {
    register,
    control,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<ProfileFormValues>({ resolver: zodResolver(profileSchema), defaultValues });
  const [banner, setBanner] = useState<string | null>(null);
  const timeZones = useMemo(() => {
    const zones = supportedTimeZones();
    return zones.includes(defaultValues.timezone) ? zones : [defaultValues.timezone, ...zones];
  }, [defaultValues.timezone]);

  async function submit(values: ProfileFormValues) {
    setBanner(null);
    try {
      await onSubmit(toProfileIn(values));
      onSaved?.();
    } catch (error) {
      const serverFields = fieldErrors(error);
      const entries = Object.entries(serverFields);
      for (const [field, message] of entries) {
        setError(field.split(".")[0] as Path<ProfileFormValues>, { type: "server", message });
      }
      setBanner(
        entries.length > 0
          ? "Please fix the highlighted fields and try again."
          : describeError(error),
      );
    }
  }

  const err = (name: keyof ProfileFormValues) => errors[name]?.message as string | undefined;

  return (
    <form onSubmit={handleSubmit(submit)} noValidate className="max-w-3xl space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>About you</CardTitle>
          <CardDescription>Used to tailor your plan. Only your name is required.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <FormField label="Name" htmlFor="name" error={err("name")} className="sm:col-span-2">
            <Input autoComplete="name" {...fieldAria("name", err("name"))} {...register("name")} />
          </FormField>
          <FormField label="College" htmlFor="college" error={err("college")} optional>
            <Input {...fieldAria("college", err("college"))} {...register("college")} />
          </FormField>
          <FormField label="Degree" htmlFor="degree" error={err("degree")} optional>
            <Input
              placeholder="B.Tech CSE"
              {...fieldAria("degree", err("degree"))}
              {...register("degree")}
            />
          </FormField>
          <FormField
            label="Year of study"
            htmlFor="current_year"
            error={err("current_year")}
            optional
          >
            <Select
              {...fieldAria("current_year", err("current_year"))}
              {...register("current_year")}
            >
              <option value="">Select…</option>
              {[1, 2, 3, 4, 5, 6].map((year) => (
                <option key={year} value={year}>
                  Year {year}
                </option>
              ))}
            </Select>
          </FormField>
          <div className="grid grid-cols-[1fr_auto] gap-3">
            <FormField label="CGPA" htmlFor="cgpa" error={err("cgpa")} optional>
              <Input
                inputMode="decimal"
                placeholder="8.75"
                {...fieldAria("cgpa", err("cgpa"))}
                {...register("cgpa")}
              />
            </FormField>
            <FormField label="Out of" htmlFor="cgpa_scale" error={err("cgpa_scale")}>
              <Select {...fieldAria("cgpa_scale", err("cgpa_scale"))} {...register("cgpa_scale")}>
                {CGPA_SCALES.map((scale) => (
                  <option key={scale} value={scale}>
                    {scale}
                  </option>
                ))}
              </Select>
            </FormField>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Skills and goals</CardTitle>
          <CardDescription>Where you want to get to.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <FormField
            label="Skills"
            htmlFor="skills"
            error={err("skills")}
            hint="Type a skill and press Enter."
            optional
            className="sm:col-span-2"
          >
            <Controller
              control={control}
              name="skills"
              render={({ field }) => (
                <TagInput
                  value={field.value}
                  onChange={field.onChange}
                  placeholder="Python, React, SQL…"
                  {...fieldAria("skills", err("skills"), true)}
                />
              )}
            />
          </FormField>
          <FormField
            label="Dream company"
            htmlFor="dream_company"
            error={err("dream_company")}
            optional
          >
            <Input
              {...fieldAria("dream_company", err("dream_company"))}
              {...register("dream_company")}
            />
          </FormField>
          <FormField label="Dream role" htmlFor="dream_role" error={err("dream_role")} optional>
            <Input
              placeholder="SWE Intern"
              {...fieldAria("dream_role", err("dream_role"))}
              {...register("dream_role")}
            />
          </FormField>
          <FormField
            label="Target package (LPA)"
            htmlFor="target_package_lpa"
            error={err("target_package_lpa")}
            optional
          >
            <Input
              inputMode="decimal"
              {...fieldAria("target_package_lpa", err("target_package_lpa"))}
              {...register("target_package_lpa")}
            />
          </FormField>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Practice setup</CardTitle>
          <CardDescription>Helps size your daily plan realistically.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <FormField
            label="Daily study time (minutes)"
            htmlFor="daily_minutes"
            error={err("daily_minutes")}
            optional
          >
            <Input
              inputMode="numeric"
              placeholder="90"
              {...fieldAria("daily_minutes", err("daily_minutes"))}
              {...register("daily_minutes")}
            />
          </FormField>
          <FormField
            label="Preferred language"
            htmlFor="preferred_language"
            error={err("preferred_language")}
            optional
          >
            <Select
              {...fieldAria("preferred_language", err("preferred_language"))}
              {...register("preferred_language")}
            >
              <option value="">Select…</option>
              {LANGUAGES.map((language) => (
                <option key={language.value} value={language.value}>
                  {language.label}
                </option>
              ))}
            </Select>
          </FormField>
          <FormField
            label="Time zone"
            htmlFor="timezone"
            error={err("timezone")}
            hint="Your day, and streaks, are based on this."
            className="sm:col-span-2"
          >
            <Select {...fieldAria("timezone", err("timezone"), true)} {...register("timezone")}>
              {timeZones.map((zone) => (
                <option key={zone} value={zone}>
                  {zone}
                </option>
              ))}
            </Select>
          </FormField>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Coding profiles</CardTitle>
          <CardDescription>
            Usernames only. We do not connect to these accounts yet.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <FormField
            label="GitHub username"
            htmlFor="github_username"
            error={err("github_username")}
            optional
          >
            <Input
              {...fieldAria("github_username", err("github_username"))}
              {...register("github_username")}
            />
          </FormField>
          <FormField
            label="LinkedIn URL"
            htmlFor="linkedin_url"
            error={err("linkedin_url")}
            optional
          >
            <Input
              inputMode="url"
              placeholder="https://linkedin.com/in/your-name"
              {...fieldAria("linkedin_url", err("linkedin_url"))}
              {...register("linkedin_url")}
            />
          </FormField>
          <FormField
            label="LeetCode username"
            htmlFor="leetcode_username"
            error={err("leetcode_username")}
            optional
          >
            <Input
              {...fieldAria("leetcode_username", err("leetcode_username"))}
              {...register("leetcode_username")}
            />
          </FormField>
          <FormField
            label="Codeforces username"
            htmlFor="codeforces_username"
            error={err("codeforces_username")}
            optional
          >
            <Input
              {...fieldAria("codeforces_username", err("codeforces_username"))}
              {...register("codeforces_username")}
            />
          </FormField>
        </CardContent>
      </Card>

      {banner ? (
        <p role="alert" className="text-sm text-danger">
          {banner}
        </p>
      ) : null}
      <Button type="submit" size="lg" disabled={isSubmitting}>
        {isSubmitting ? "Saving…" : submitLabel}
      </Button>
    </form>
  );
}
