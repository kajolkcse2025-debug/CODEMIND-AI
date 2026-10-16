/**
 * Only same-site absolute paths may be used as a post-login destination.
 *
 * Browsers treat "//host" and "/\host" as protocol-relative URLs (and strip tabs/newlines
 * inside URLs), so a naive `startsWith("/")` check would allow redirects off-site.
 */
const SAFE_PATH = /^\/(?![/\\])\S*$/;

export function safeRedirectPath(candidate: unknown, fallback = "/dashboard"): string {
  return typeof candidate === "string" && SAFE_PATH.test(candidate) ? candidate : fallback;
}
