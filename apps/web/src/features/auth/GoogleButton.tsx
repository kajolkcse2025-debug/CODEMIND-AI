import { useState } from "react";

import { Button } from "@/components/ui/button";
import { useAuth } from "@/features/auth/auth-context";
import { authErrorMessage } from "@/features/auth/firebaseErrors";

export function GoogleButton({ onError }: { onError: (message: string | null) => void }) {
  const { signInWithGoogle, firebaseConfigured } = useAuth();
  const [busy, setBusy] = useState(false);

  async function handleClick() {
    setBusy(true);
    onError(null);
    try {
      await signInWithGoogle();
    } catch (error) {
      onError(authErrorMessage(error));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Button
      variant="outline"
      className="w-full"
      onClick={handleClick}
      disabled={busy || !firebaseConfigured}
    >
      <svg viewBox="0 0 24 24" className="size-4" aria-hidden="true">
        <path
          fill="currentColor"
          d="M21.35 11.1H12v2.98h5.35c-.23 1.4-1.64 4.1-5.35 4.1-3.22 0-5.85-2.67-5.85-5.95s2.63-5.95 5.85-5.95c1.83 0 3.06.78 3.76 1.45l2.56-2.47C16.68 3.77 14.55 2.8 12 2.8 6.92 2.8 2.8 6.92 2.8 12S6.92 21.2 12 21.2c5.27 0 8.76-3.7 8.76-8.92 0-.6-.07-1.06-.16-1.18z"
        />
      </svg>
      Continue with Google
    </Button>
  );
}
