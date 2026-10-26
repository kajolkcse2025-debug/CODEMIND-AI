
import { api } from "@/lib/api";

export type AssessmentLanguage = "python" | "java" | "cpp";

export interface AssessmentQuestion {
  slug: string;
  title: string;
  topic: string;
  difficulty: "easy" | "medium" | "hard";
  statement: string;
  time_limit_sec: number;
}

export interface AssessmentQuestionsResponse {
  total: number;
  questions: AssessmentQuestion[];
  summary?: unknown;
}

export interface AssessmentSubmissionResult {
  question_slug: string;
  verdict:
    | "accepted"
    | "wrong_answer"
    | "runtime_error"
    | "time_limit"
    | "memory_limit"
    | "compile_error"
    | "runner_unavailable";
  verified: boolean;
  counts_toward_metrics: boolean;
  tests_passed: number;
  tests_total: number;
  detail?: string | null;
}

export function getAssessmentQuestions(
  count = 8,
): Promise<AssessmentQuestionsResponse> {
  return api.get(
    `/api/v1/coding-assessment/questions?count=${count}`,
  );
}

export function submitAssessmentCode(
  slug: string,
  payload: {
    language: AssessmentLanguage;
    source_code: string;
  },
): Promise<AssessmentSubmissionResult> {
  return api.post(
    `/api/v1/coding-assessment/${encodeURIComponent(slug)}/submit`,
    payload,
  );
}
