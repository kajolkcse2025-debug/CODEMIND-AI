/** The backend's single error envelope: { error: { code, message, details, request_id } }. */
export interface ApiErrorInit {
  status: number;
  code: string;
  message: string;
  details?: Record<string, unknown>;
  requestId?: string | null;
  retryAfterSeconds?: number | null;
}

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details: Record<string, unknown>;
  readonly requestId: string | null;
  readonly retryAfterSeconds: number | null;

  constructor(init: ApiErrorInit) {
    super(init.message);
    this.name = "ApiError";
    this.status = init.status;
    this.code = init.code;
    this.details = init.details ?? {};
    this.requestId = init.requestId ?? null;
    this.retryAfterSeconds = init.retryAfterSeconds ?? null;
  }

  get isNetworkError(): boolean {
    return this.status === 0;
  }
  get isRateLimited(): boolean {
    return this.status === 429;
  }
  get isUnauthenticated(): boolean {
    return this.status === 401;
  }
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

/** Field-level validation messages from a 422 response, keyed by field name. */
export function fieldErrors(error: unknown): Record<string, string> {
  if (!isApiError(error) || error.code !== "validation_error") return {};
  const list = error.details["errors"];
  if (!Array.isArray(list)) return {};
  const result: Record<string, string> = {};
  for (const item of list) {
    if (item && typeof item === "object") {
      const { field, issue } = item as { field?: unknown; issue?: unknown };
      if (typeof field === "string" && typeof issue === "string" && field && !(field in result)) {
        result[field] = issue;
      }
    }
  }
  return result;
}

/** A message that is safe to show to a student. */
export function describeError(error: unknown): string {
  if (isApiError(error)) {
    if (error.isNetworkError)
      return "We could not reach the server. Check your connection and try again.";
    if (error.isRateLimited) {
      return error.retryAfterSeconds
        ? `Too many requests. Please wait ${error.retryAfterSeconds} seconds and try again.`
        : "Too many requests. Please wait a moment and try again.";
    }
    return error.message;
  }
  return "Something unexpected happened. Please try again.";
}
