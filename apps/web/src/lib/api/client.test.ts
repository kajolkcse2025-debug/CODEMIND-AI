import { describe, expect, it, vi } from "vitest";

import { ApiClient } from "@/lib/api/client";
import { ApiError, describeError, fieldErrors } from "@/lib/api/errors";

function json(body: unknown, init: ResponseInit = {}): Response {
  return new Response(JSON.stringify(body), {
    headers: { "Content-Type": "application/json", ...(init.headers as Record<string, string>) },
    ...init,
  });
}

function envelope(code: string, message: string, details: Record<string, unknown> = {}) {
  return { error: { code, message, details, request_id: "req-123" } };
}

function setup(responses: Response[], token: string | null = "tok-1") {
  const fetchImpl = vi.fn<typeof fetch>();
  for (const response of responses) fetchImpl.mockResolvedValueOnce(response);
  const getToken = vi.fn(async (force: boolean) =>
    token ? (force ? "tok-refreshed" : token) : null,
  );
  const client = new ApiClient({ baseUrl: "http://api.test", getToken, fetchImpl });
  return { client, fetchImpl, getToken };
}

const authHeader = (fetchImpl: ReturnType<typeof vi.fn>, call: number) =>
  new Headers((fetchImpl.mock.calls[call]![1] as RequestInit).headers).get("Authorization");

describe("ApiClient", () => {
  it("attaches the Firebase token and returns typed JSON", async () => {
    const { client, fetchImpl } = setup([json({ status: "ok" })]);
    const result = await client.get<{ status: string }>("/api/v1/health");
    expect(result).toEqual({ status: "ok" });
    expect(fetchImpl.mock.calls[0]![0]).toBe("http://api.test/api/v1/health");
    expect(authHeader(fetchImpl, 0)).toBe("Bearer tok-1");
  });

  it("sends JSON bodies with the right method and content type", async () => {
    const { client, fetchImpl } = setup([json({ ok: true }, { status: 201 })]);
    await client.post("/api/v1/profile", { name: "Asha" });
    const init = fetchImpl.mock.calls[0]![1] as RequestInit;
    expect(init.method).toBe("POST");
    expect(init.body).toBe(JSON.stringify({ name: "Asha" }));
    expect(new Headers(init.headers).get("Content-Type")).toBe("application/json");
  });

  it("omits the Authorization header for public requests", async () => {
    const { client, fetchImpl, getToken } = setup([json({ status: "ok" })]);
    await client.get("/api/v1/health", { auth: false });
    expect(getToken).not.toHaveBeenCalled();
    expect(authHeader(fetchImpl, 0)).toBeNull();
  });

  it("builds query strings and skips undefined values", async () => {
    const { client, fetchImpl } = setup([json({})]);
    await client.get("/x", { query: { a: 1, b: undefined, c: "z" } });
    expect(fetchImpl.mock.calls[0]![0]).toBe("http://api.test/x?a=1&c=z");
  });

  it("on 401 refreshes the token once and retries once", async () => {
    const { client, fetchImpl, getToken } = setup([
      json(envelope("unauthenticated", "expired"), { status: 401 }),
      json({ id: 1 }),
    ]);
    const onUnauth = vi.fn();
    client.setUnauthenticatedHandler(onUnauth);
    await expect(client.get("/api/v1/me")).resolves.toEqual({ id: 1 });
    expect(fetchImpl).toHaveBeenCalledTimes(2);
    expect(getToken).toHaveBeenNthCalledWith(1, false);
    expect(getToken).toHaveBeenNthCalledWith(2, true);
    expect(authHeader(fetchImpl, 1)).toBe("Bearer tok-refreshed");
    expect(onUnauth).not.toHaveBeenCalled();
  });

  it("signs out when the retry is still 401, and never retries a second time", async () => {
    const { client, fetchImpl } = setup([
      json(envelope("unauthenticated", "no"), { status: 401 }),
      json(envelope("unauthenticated", "still no"), { status: 401 }),
    ]);
    const onUnauth = vi.fn();
    client.setUnauthenticatedHandler(onUnauth);
    await expect(client.get("/api/v1/me")).rejects.toMatchObject({ status: 401 });
    expect(fetchImpl).toHaveBeenCalledTimes(2);
    expect(onUnauth).toHaveBeenCalledTimes(1);
  });

  it("does not loop when there is no token at all", async () => {
    const { client, fetchImpl } = setup(
      [json(envelope("unauthenticated", "no"), { status: 401 })],
      null,
    );
    await expect(client.get("/api/v1/me")).rejects.toBeInstanceOf(ApiError);
    expect(fetchImpl).toHaveBeenCalledTimes(1);
  });

  it("surfaces 429 with Retry-After and does not retry", async () => {
    const { client, fetchImpl } = setup([
      json(envelope("rate_limited", "Slow down"), {
        status: 429,
        headers: { "Retry-After": "12" },
      }),
    ]);
    const error = await client.get("/x").catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ status: 429, code: "rate_limited", retryAfterSeconds: 12 });
    expect((error as ApiError).isRateLimited).toBe(true);
    expect(describeError(error)).toContain("12 seconds");
    expect(fetchImpl).toHaveBeenCalledTimes(1);
  });

  it("parses the standard error envelope", async () => {
    const { client } = setup([
      json(envelope("profile_not_found", "No profile yet."), {
        status: 404,
        headers: { "X-Request-ID": "hdr-1" },
      }),
    ]);
    const error = (await client.get("/api/v1/profile").catch((e: unknown) => e)) as ApiError;
    expect(error).toMatchObject({ status: 404, code: "profile_not_found", requestId: "req-123" });
    expect(error.message).toBe("No profile yet.");
  });

  it("falls back gracefully for non-JSON error bodies and uses the header request id", async () => {
    const { client } = setup([
      new Response("<html>Bad gateway</html>", {
        status: 502,
        headers: { "X-Request-ID": "hdr-9" },
      }),
    ]);
    const error = (await client.get("/x").catch((e: unknown) => e)) as ApiError;
    expect(error).toMatchObject({ status: 502, code: "server_error", requestId: "hdr-9" });
    expect(error.message).not.toContain("html");
  });

  it("turns network failures into a typed network error", async () => {
    const fetchImpl = vi.fn<typeof fetch>().mockRejectedValue(new TypeError("Failed to fetch"));
    const client = new ApiClient({
      baseUrl: "http://api.test",
      getToken: async () => null,
      fetchImpl,
    });
    const error = (await client.get("/x", { auth: false }).catch((e: unknown) => e)) as ApiError;
    expect(error).toMatchObject({ status: 0, code: "network_error" });
    expect(error.isNetworkError).toBe(true);
  });

  it("handles 204 No Content", async () => {
    const { client } = setup([new Response(null, { status: 204 })]);
    await expect(client.delete("/x")).resolves.toBeUndefined();
  });
});

describe("error helpers", () => {
  it("extracts field-level validation messages", () => {
    const error = new ApiError({
      status: 422,
      code: "validation_error",
      message: "bad",
      details: {
        errors: [
          { field: "cgpa", issue: "too high" },
          { field: "cgpa", issue: "second" },
          { field: "timezone", issue: "unknown zone" },
        ],
      },
    });
    expect(fieldErrors(error)).toEqual({ cgpa: "too high", timezone: "unknown zone" });
  });

  it("returns nothing for other errors", () => {
    expect(fieldErrors(new Error("x"))).toEqual({});
    expect(fieldErrors(new ApiError({ status: 404, code: "not_found", message: "x" }))).toEqual({});
  });

  it("describes unknown errors generically", () => {
    expect(describeError(new Error("secret internals"))).not.toContain("secret");
  });
});
