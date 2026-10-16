import { QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactElement } from "react";
import { RouterProvider } from "react-router-dom";

import { createTestRouter } from "@/app/router";
import { AuthContext, type AuthContextValue } from "@/features/auth/auth-context";
import { createQueryClient } from "@/lib/queryClient";
import { ThemeProvider } from "@/lib/theme";

export function fakeAuth(overrides: Partial<AuthContextValue> = {}): AuthContextValue {
  return {
    status: "unauthenticated",
    user: null,
    firebaseConfigured: true,
    signInWithEmail: async () => undefined,
    registerWithEmail: async () => undefined,
    signInWithGoogle: async () => undefined,
    sendPasswordReset: async () => undefined,
    resendVerification: async () => undefined,
    reloadUser: async () => undefined,
    signOut: async () => undefined,
    ...overrides,
  };
}

export function renderWithProviders(ui: ReactElement, auth: Partial<AuthContextValue> = {}) {
  const client = createQueryClient();
  return render(
    <ThemeProvider>
      <QueryClientProvider client={client}>
        <AuthContext.Provider value={fakeAuth(auth)}>{ui}</AuthContext.Provider>
      </QueryClientProvider>
    </ThemeProvider>,
  );
}

export function renderRoute(path: string, auth: Partial<AuthContextValue> = {}, state?: unknown) {
  const router = createTestRouter([{ pathname: path, state }]);
  const result = renderWithProviders(<RouterProvider router={router} />, auth);
  return { ...result, router };
}
