import { ApiError } from "@/lib/api/errors";

export type QueryValue = string | number | boolean | null | undefined;

export interface RequestOptions {
  method?: "GET" | "POST" | "PUT" | "DELETE";
  body?: unknown;
  query?: Record<string, QueryValue>;
  signal?: AbortSignal;
  /** Set false for public endpoints. Default true. */
  auth?: boolean;
}

type ShortcutOptions = Omit<RequestOptions, "method" | "body">;

export interface ApiClientOptions {
  baseUrl: string;
  /** Returns a Firebase ID token, or null when signed out. ``forceRefresh`` bypasses the cache. */
  getToken: (forceRefresh: boolean) => Promise<string | null>;
  fetchImpl?: typeof fetch;
  timeoutMs?: number;
}

const STATUS_CODES: Record<number, string> = {
  400: "bad_request",
  401: "unauthenticated",
  403: "forbidden",
  404: "not_found",
  409: "conflict",
  422: "validation_error",
  429: "rate_limited",
};

/**
 * The ONE place the app talks to the backend. It:
 *  - attaches the Firebase ID token,
 *  - on 401 refreshes the token once and retries once, then signs the user out,
 *  - turns 429 into an ApiError carrying Retry-After (it never retries blindly),
 *  - parses the standard error envelope into ApiError,
 *  - returns typed responses.
 */
export class ApiClient {
  private readonly options: ApiClientOptions;
  private onUnauthenticated: (() => void) | null = null;

  constructor(options: ApiClientOptions) {
    this.options = options;
  }

  setUnauthenticatedHandler(handler: (() => void) | null): void {
    this.onUnauthenticated = handler;
  }

  get<T>(path: string, options: ShortcutOptions = {}): Promise<T> {
    return this.request<T>(path, { ...options, method: "GET" });
  }
  post<T>(path: string, body?: unknown, options: ShortcutOptions = {}): Promise<T> {
    return this.request<T>(path, { ...options, method: "POST", body });
  }
  put<T>(path: string, body?: unknown, options: ShortcutOptions = {}): Promise<T> {
    return this.request<T>(path, { ...options, method: "PUT", body });
  }
  delete<T>(path: string, options: ShortcutOptions = {}): Promise<T> {
    return this.request<T>(path, { ...options, method: "DELETE" });
  }

  async request<T>(path: string, init: RequestOptions = {}): Promise<T> {
    const { method = "GET", body, query, signal, auth = true } = init;
    const url = this.buildUrl(path, query);
    let refreshed = false;

    for (;;) {
      const headers = new Headers({ Accept: "application/json" });
      if (body !== undefined) headers.set("Content-Type", "application/json");

      let hadToken = false;
      if (auth) {
        const token = await this.options.getToken(refreshed);
        if (token) {
          headers.set("Authorization", `Bearer ${token}`);
          hadToken = true;
        }
      }

      const response = await this.send(url, {
        method,
        headers,
        body: body === undefined ? undefined : JSON.stringify(body),
        signal,
      });

      if (response.status === 401 && auth && hadToken && !refreshed) {
        refreshed = true; // refresh the token once, retry once
        continue;
      }
      if (response.ok) return (await this.parseSuccess<T>(response)) as T;

      const error = await this.parseError(response);
      if (response.status === 401 && auth) this.onUnauthenticated?.();
      throw error;
    }
  }

  private buildUrl(path: string, query?: Record<string, QueryValue>): string {
    const search = new URLSearchParams();
    for (const [key, value] of Object.entries(query ?? {})) {
      if (value !== undefined && value !== null) search.set(key, String(value));
    }
    const qs = search.toString();
    return `${this.options.baseUrl}${path}${qs ? `?${qs}` : ""}`;
  }

  private async send(url: string, init: RequestInit): Promise<Response> {
    const fetchImpl = this.options.fetchImpl ?? fetch;
    const controller = new AbortController();
    const external = init.signal;
    const onExternalAbort = () => controller.abort();
    if (external) {
      if (external.aborted) controller.abort();
      else external.addEventListener("abort", onExternalAbort, { once: true });
    }
    const timer = setTimeout(() => controller.abort(), this.options.timeoutMs ?? 30_000);
    try {
      return await fetchImpl(url, { ...init, signal: controller.signal });
    } catch (cause) {
      if (external?.aborted) throw cause; // the caller cancelled; not an error to report
      throw new ApiError({
        status: 0,
        code: "network_error",
        message: "We could not reach the server.",
      });
    } finally {
      clearTimeout(timer);
      external?.removeEventListener("abort", onExternalAbort);
    }
  }

  private async parseSuccess<T>(response: Response): Promise<T | undefined> {
    if (response.status === 204) return undefined;
    const text = await response.text();
    return text ? (JSON.parse(text) as T) : undefined;
  }

  private async parseError(response: Response): Promise<ApiError> {
    const requestId = response.headers.get("x-request-id");
    const retryHeader = Number(response.headers.get("retry-after"));
    const retryAfterSeconds = Number.isFinite(retryHeader) && retryHeader > 0 ? retryHeader : null;

    let envelope: unknown = null;
    try {
      envelope = await response.json();
    } catch {
      /* non-JSON error body (for example a proxy error page) */
    }
    const inner =
      envelope && typeof envelope === "object" && "error" in envelope
        ? (envelope as { error: Record<string, unknown> }).error
        : null;

    if (inner && typeof inner["code"] === "string" && typeof inner["message"] === "string") {
      return new ApiError({
        status: response.status,
        code: inner["code"],
        message: inner["message"],
        details: (inner["details"] as Record<string, unknown> | undefined) ?? {},
        requestId: (inner["request_id"] as string | null | undefined) ?? requestId,
        retryAfterSeconds,
      });
    }
    return new ApiError({
      status: response.status,
      code:
        STATUS_CODES[response.status] ?? (response.status >= 500 ? "server_error" : "http_error"),
      message:
        response.status >= 500
          ? "The server had a problem. Please try again shortly."
          : "The request could not be completed.",
      requestId,
      retryAfterSeconds,
    });
  }
}
