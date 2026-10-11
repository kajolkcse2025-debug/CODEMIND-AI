import { useState } from "react";

import { ErrorState } from "@/components/shared/ErrorState";
import { LoadingSkeleton } from "@/components/shared/LoadingSkeleton";
import { PageHeader } from "@/components/shared/PageHeader";
import { useProfile, useUpdateProfile } from "@/features/profile/hooks";
import { ProfileForm } from "@/features/profile/ProfileForm";
import { toFormValues } from "@/features/profile/schema";

export function ProfilePage() {
  const profile = useProfile();
  const update = useUpdateProfile();
  const [saved, setSaved] = useState(false);

  return (
    <>
      <PageHeader eyebrow="Account" title="Profile" description="Your goals and practice setup." />
      {profile.isPending ? (
        <LoadingSkeleton variant="card" label="Loading your profile" />
      ) : profile.isError ? (
        <ErrorState
          title="Could not load your profile"
          error={profile.error}
          onRetry={() => void profile.refetch()}
        />
      ) : (
        <>
          {saved ? (
            <p role="status" className="mb-4 text-sm text-success">
              Profile saved.
            </p>
          ) : null}
          <ProfileForm
            // Re-mount with fresh defaults after a save so the form reflects server-normalised data.
            key={profile.dataUpdatedAt}
            defaultValues={toFormValues(profile.data)}
            submitLabel="Save changes"
            onSubmit={(payload) => {
              setSaved(false);
              return update.mutateAsync(payload);
            }}
            onSaved={() => setSaved(true)}
          />
        </>
      )}
    </>
  );
}
