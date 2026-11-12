
import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import { useAuth } from "@/features/auth/auth-context";
import {
  completeRoadmapItem,
  fetchRoadmap,
} from "@/features/roadmap/api";

export function useRoadmap(dailyMinutes = 45) {
  const { status } = useAuth();

  return useQuery({
    queryKey: ["roadmap", dailyMinutes],
    queryFn: () => fetchRoadmap(dailyMinutes),
    enabled: status === "authenticated",
  });
}

export function useCompleteRoadmapItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: completeRoadmapItem,
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["roadmap"],
      });
    },
  });
}
