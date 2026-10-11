import { TriangleAlert } from "lucide-react";
import type { ReactNode } from "react";
import { Link } from "react-router-dom";

import { Wordmark } from "@/components/shared/Brand";
import { ThemeToggle } from "@/components/shared/ThemeToggle";
import { useAuth } from "@/features/auth/auth-context";

interface AuthLayoutProps {
  title: string;
  description: string;
  children: ReactNode;
  footer?: ReactNode;
}

export function AuthLayout({ title, description, children, footer }: AuthLayoutProps) {
  const { firebaseConfigured } = useAuth();
  return (
    <div className="flex min-h-svh flex-col">
      <header className="flex items-center justify-between px-6 py-4">
        <Link to="/" aria-label="CodeMind home">
          <Wordmark />
        </Link>
        <ThemeToggle />
      </header>
      <main className="flex flex-1 items-center justify-center px-4 pb-16">
        <div className="w-full max-w-sm">
          <h1 className="text-2xl font-semibold">{title}</h1>
          <p className="mt-2 text-sm text-muted-foreground">{description}</p>
          {!firebaseConfigured ? (
            <div
              role="alert"
              className="mt-6 flex gap-3 rounded-md border border-warning/40 bg-warning/10 p-3 text-sm"
            >
              <TriangleAlert className="mt-0.5 size-4 shrink-0 text-warning" aria-hidden="true" />
              <p>
                Firebase is not configured for this build, so sign-in is unavailable. Copy{" "}
                <code className="font-mono text-xs">apps/web/.env.example</code> to{" "}
                <code className="font-mono text-xs">.env</code> and fill in the Firebase values.
              </p>
            </div>
          ) : null}
          <div className="mt-6">{children}</div>
          {footer ? (
            <div className="mt-6 text-center text-sm text-muted-foreground">{footer}</div>
          ) : null}
        </div>
      </main>
    </div>
  );
}
