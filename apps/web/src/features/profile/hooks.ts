import type { MeResponse, ProfileOut } from "@codemind/shared";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { useAuth } from "@/features/auth/auth-context";
import { createProfile, fetchProfile, updateProfile } from "@/features/profile/api";
import { queryKeys } from "@/lib/queryKeys";

export function useProfile() {
  const { status } = useAuth();
  return useQuery({
    queryKey: queryKeys.profile,
    queryFn: fetchProfile,
    enabled: status === "authenticated",
  });
}

function useProfileMutation(fn: typeof createProfile) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: fn,
    onSuccess: (profile: ProfileOut) => {
      queryClient.setQueryData(queryKeys.profile, profile);
      // Keep GET /me consistent (it embeds the profile and onboarding status).
      queryClient.setQueryData<MeResponse>(queryKeys.me, (current) =>
        current ? { ...current, profile } : current,
      );
      void queryClient.invalidateQueries({ queryKey: queryKeys.me });
    },
  });
}

export const useCreateProfile = () => useProfileMutation(createProfile);
export const useUpdateProfile = () => useProfileMutation(updateProfile);
