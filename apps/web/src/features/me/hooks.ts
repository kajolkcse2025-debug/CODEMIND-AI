import { useQuery } from "@tanstack/react-query";

import { useAuth } from "@/features/auth/auth-context";
import { fetchMe } from "@/features/me/api";
import { queryKeys } from "@/lib/queryKeys";

/** The authenticated application user (and profile, if any), straight from GET /me. */
export function useMe() {
  const { status } = useAuth();
  return useQuery({
    queryKey: queryKeys.me,
    queryFn: fetchMe,
    enabled: status === "authenticated",
  });
}
