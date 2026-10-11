import { useMemo } from "react";
import { useNavigate } from "react-router-dom";

import { PageHeader } from "@/components/shared/PageHeader";
import { Wordmark } from "@/components/shared/Brand";
import { ThemeToggle } from "@/components/shared/ThemeToggle";
import { useCreateProfile } from "@/features/profile/hooks";
import { ProfileForm } from "@/features/profile/ProfileForm";
import { emptyProfileValues } from "@/features/profile/schema";

export function OnboardingPage() {
  const navigate = useNavigate();
  const create = useCreateProfile();
  const defaults = useMemo(emptyProfileValues, []);
  return (
    <div className="mx-auto min-h-svh max-w-3xl px-4 pb-16">
      <div className="flex items-center justify-between py-4">
        <Wordmark />
        <ThemeToggle />
      </div>
      <PageHeader
        eyebrow="Welcome"
        title="Set up your profile"
        description="Tell us about your goals so your plan can fit your life. You can change all of this later."
      />
      <ProfileForm
        defaultValues={defaults}
        submitLabel="Save and continue"
        onSubmit={(payload) => create.mutateAsync(payload)}
        onSaved={() => navigate("/dashboard", { replace: true })}
      />
    </div>
  );
}
