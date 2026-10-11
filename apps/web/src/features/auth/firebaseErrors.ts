import { FirebaseNotConfiguredError } from "@/lib/firebase";

/**
 * Friendly, non-leaking messages for Firebase Auth failures.
 * Returns null for outcomes that should be silent (for example the student closed the popup).
 */
export function authErrorMessage(error: unknown): string | null {
  if (error instanceof FirebaseNotConfiguredError) return error.message;
  const code =
    error && typeof error === "object" && "code" in error
      ? String((error as { code: unknown }).code)
      : "";
  switch (code) {
    case "auth/invalid-credential":
    case "auth/wrong-password":
    case "auth/user-not-found":
    case "auth/invalid-email":
      return "Incorrect email or password.";
    case "auth/email-already-in-use":
      return "An account with this email already exists. Try signing in instead.";
    case "auth/weak-password":
      return "Choose a stronger password (at least 8 characters).";
    case "auth/too-many-requests":
      return "Too many attempts. Wait a few minutes and try again.";
    case "auth/network-request-failed":
      return "We could not reach the sign-in service. Check your connection.";
    case "auth/popup-closed-by-user":
    case "auth/cancelled-popup-request":
      return null;
    case "auth/popup-blocked":
      return "Your browser blocked the Google sign-in popup. Allow popups and try again.";
    case "auth/account-exists-with-different-credential":
      return "This email is registered with a different sign-in method.";
    default:
      return "Something went wrong while signing in. Please try again.";
  }
}
