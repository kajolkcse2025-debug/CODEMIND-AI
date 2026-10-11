import { useQueryClient } from "@tanstack/react-query";
import {
  GoogleAuthProvider,
  createUserWithEmailAndPassword,
  onAuthStateChanged,
  sendEmailVerification,
  sendPasswordResetEmail,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut as firebaseSignOut,
  type User,
} from "firebase/auth";
import { useCallback, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { AuthContext, type AuthContextValue, type AuthStatus } from "@/features/auth/auth-context";
import { api } from "@/lib/api";
import { isFirebaseConfigured } from "@/lib/env";
import { firebaseAuth, requireFirebaseAuth } from "@/lib/firebase";

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const [status, setStatus] = useState<AuthStatus>(firebaseAuth ? "loading" : "unauthenticated");
  const [user, setUser] = useState<User | null>(null);
  // Firebase mutates the same User object when it reloads; bump to re-render consumers.
  const [, setVersion] = useState(0);

  useEffect(() => {
    if (!firebaseAuth) return;
    return onAuthStateChanged(firebaseAuth, (next) => {
      setUser(next);
      setStatus(next ? "authenticated" : "unauthenticated");
      if (!next) queryClient.clear(); // never keep one student's data after sign-out
    });
  }, [queryClient]);

  const signOut = useCallback(async () => {
    if (firebaseAuth) await firebaseSignOut(firebaseAuth);
  }, []);

  useEffect(() => {
    // The API client signs the user out when a request is still 401 after a token refresh.
    api.setUnauthenticatedHandler(() => void signOut());
    return () => api.setUnauthenticatedHandler(null);
  }, [signOut]);

  const value = useMemo<AuthContextValue>(
    () => ({
      status,
      user,
      firebaseConfigured: isFirebaseConfigured,
      signInWithEmail: async (email, password) => {
        await signInWithEmailAndPassword(requireFirebaseAuth(), email, password);
      },
      registerWithEmail: async (email, password) => {
        const credential = await createUserWithEmailAndPassword(
          requireFirebaseAuth(),
          email,
          password,
        );
        try {
          await sendEmailVerification(credential.user);
        } catch {
          /* the banner lets the student resend; do not fail registration over this */
        }
      },
      signInWithGoogle: async () => {
        await signInWithPopup(requireFirebaseAuth(), new GoogleAuthProvider());
      },
      sendPasswordReset: async (email) => {
        await sendPasswordResetEmail(requireFirebaseAuth(), email);
      },
      resendVerification: async () => {
        const current = requireFirebaseAuth().currentUser;
        if (current) await sendEmailVerification(current);
      },
      reloadUser: async () => {
        const current = requireFirebaseAuth().currentUser;
        if (current) {
          await current.reload();
          setVersion((n) => n + 1);
        }
      },
      signOut,
    }),
    [status, user, signOut],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
