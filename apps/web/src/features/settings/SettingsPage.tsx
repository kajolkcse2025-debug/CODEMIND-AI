import { Monitor, Moon, Sun } from "lucide-react";
import { useState } from "react";

import { PageHeader } from "@/components/shared/PageHeader";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/features/auth/auth-context";
import { useTheme, type Theme } from "@/lib/theme-context";
import { cn } from "@/lib/utils";

const themes: { value: Theme; label: string; icon: typeof Sun }[] = [
  { value: "light", label: "Light", icon: Sun },
  { value: "dark", label: "Dark", icon: Moon },
  { value: "system", label: "System", icon: Monitor },
];

export function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const { user, signOut, resendVerification } = useAuth();
  const [notice, setNotice] = useState<string | null>(null);

  async function resend() {
    try {
      await resendVerification();
      setNotice("Verification email sent.");
    } catch {
      setNotice("Could not send the email right now. Try again in a minute.");
    }
  }

  return (
    <>
      <PageHeader eyebrow="Account" title="Settings" description="Appearance and account." />
      <div className="max-w-2xl space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Appearance</CardTitle>
            <CardDescription>Dark is the default.</CardDescription>
          </CardHeader>
          <CardContent>
            <div role="radiogroup" aria-label="Theme" className="grid grid-cols-3 gap-2">
              {themes.map(({ value, label, icon: Icon }) => (
                <button
                  key={value}
                  type="button"
                  role="radio"
                  aria-checked={theme === value}
                  onClick={() => setTheme(value)}
                  className={cn(
                    "flex items-center justify-center gap-2 rounded-md border px-3 py-2.5 text-sm transition-colors hover:bg-muted",
                    theme === value && "border-primary bg-accent text-accent-foreground",
                  )}
                >
                  <Icon className="size-4" aria-hidden="true" />
                  {label}
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Account</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <p className="text-muted-foreground">Email</p>
                <p className="font-medium">{user?.email ?? "Not available"}</p>
              </div>
              {user?.emailVerified ? (
                <Badge variant="success">Verified</Badge>
              ) : (
                <Button variant="outline" size="sm" onClick={() => void resend()}>
                  Resend verification
                </Button>
              )}
            </div>
            {notice ? (
              <p role="status" className="text-xs text-muted-foreground">
                {notice}
              </p>
            ) : null}
            <Button variant="outline" onClick={() => void signOut()}>
              Sign out
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Privacy and data</CardTitle>
            <CardDescription>
              Data export and account deletion are planned but not built yet.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    </>
  );
}
