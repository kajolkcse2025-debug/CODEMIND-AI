
import { api } from "@/lib/api";

export interface RoadmapItem {
  id: string;
  position: number;
  phase: string;
  topic_id: number;
  title: string;
  type: "learn" | "practice" | "revise" | "project" | "milestone";
  target_problems: number;
  completed_problems: number;
  status: "upcoming" | "active" | "done" | "skipped";
  reason: {
    mastery: number;
    attempts: number;
    confidence: number;
    explanation: string;
  };
  due_date: string | null;
}

export interface RoadmapResponse {
  roadmap_id: string;
  status: string;
  daily_minutes: number;
  total_topics: number;
  completed_topics: number;
  progress_percentage: number;
  rationale: string;
  items: RoadmapItem[];
}

export const fetchRoadmap = (dailyMinutes = 45) =>
  api.get<RoadmapResponse>(
    `/api/v1/roadmap?daily_minutes=${dailyMinutes}`,
  );

export const completeRoadmapItem = (itemId: string) =>
  api.put(`/api/v1/roadmap/${itemId}/complete`, {});
