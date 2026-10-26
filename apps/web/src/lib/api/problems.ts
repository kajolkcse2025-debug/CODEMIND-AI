
import { api } from "@/lib/api";

export interface CodingProblem {
  id: string;
  slug: string;
  title: string;
  difficulty: "easy" | "medium" | "hard";
  description: string;
}

export interface ProblemListResponse {
  items: CodingProblem[];
  total: number;
}

export interface ProblemDetail extends CodingProblem {
  input_format?: string;
  output_format?: string;
  constraints?: string[];
  examples?: Array<{
    input: string;
    output: string;
    explanation?: string;
  }>;
}

export interface SubmissionResult {
  verdict:
    | "accepted"
    | "wrong_answer"
    | "runtime_error"
    | "time_limit"
    | "memory_limit"
    | "compile_error"
    | "runner_unavailable";
  verified: boolean;
  tests_passed: number;
  tests_total: number;
  detail?: string | null;
}

export function listProblems(): Promise<ProblemListResponse> {
  return api.get("/api/v1/problems");
}

export function getProblem(slug: string): Promise<ProblemDetail> {
  return api.get(`/api/v1/problems/${encodeURIComponent(slug)}`);
}

export interface SubmitCode {
  language: "python" | "java" | "cpp";
  source_code: string;
}

export function submitCode(
  slug: string,
  payload: SubmitCode,
): Promise<SubmissionResult> {
  return api.post(
    `/api/v1/problems/${encodeURIComponent(slug)}/submissions`,
    payload,
  );
}
