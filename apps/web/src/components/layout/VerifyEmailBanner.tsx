import { MailWarning } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { useAuth } from "@/features/auth/auth-context";

/** Shown to signed-in students whose email is unverified. Verification is required for AI features later. */
export function VerifyEmailBanner() {
  const { user, resendVerification, reloadUser } = useAuth();
  const [message, setMessage] = useState<string | null>(null);

  if (!user || user.emailVerified || !user.email) return null;

  async function resend() {
    try {
      await resendVerification();
      setMessage("Verification email sent. Check your inbox.");
    } catch {
      setMessage("Could not send the email right now. Try again in a minute.");
    }
  }

  async function refresh() {
    await reloadUser();
    setMessage(null);
  }

  return (
    <div
      role="status"
      className="flex flex-wrap items-center gap-x-4 gap-y-2 border-b border-warning/30 bg-warning/10 px-4 py-2.5 text-sm lg:px-8"
    >
      <MailWarning className="size-4 shrink-0 text-warning" aria-hidden="true" />
      <p className="flex-1">
        Please verify <span className="font-medium">{user.email}</span>. Some features will need a
        verified email.
        {message ? <span className="ml-2 text-muted-foreground">{message}</span> : null}
      </p>
      <div className="flex gap-2">
        <Button size="sm" variant="outline" onClick={() => void resend()}>
          Resend email
        </Button>
        <Button size="sm" variant="ghost" onClick={() => void refresh()}>
          I have verified
        </Button>
      </div>
    </div>
  );
}
