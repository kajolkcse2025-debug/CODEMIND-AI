import { Navigate, Outlet, useLocation } from "react-router-dom";

import { ErrorState } from "@/components/shared/ErrorState";
import { LoadingSkeleton } from "@/components/shared/LoadingSkeleton";
import { safeRedirectPath } from "@/app/safe-redirect";
import { useAuth } from "@/features/auth/auth-context";
import { useMe } from "@/features/me/hooks";

function FullPageLoading({ label }: { label: string }) {
  return (
    <div className="mx-auto max-w-3xl p-8">
      <LoadingSkeleton variant="page" label={label} />
    </div>
  );
}

/** The route guards improve UX only. The backend is the sole authority on access. */
export function RequireAuth() {
  const { status } = useAuth();
  const location = useLocation();
  if (status === "loading") return <FullPageLoading label="Checking your session" />;
  if (status === "unauthenticated") {
    return <Navigate to="/login" replace state={{ from: location.pathname + location.search }} />;
  }
  return <Outlet />;
}

export function PublicOnly() {
  const { status } = useAuth();
  const location = useLocation();
  if (status === "loading") return <FullPageLoading label="Checking your session" />;
  if (status === "authenticated") {
    const from = (location.state as { from?: unknown } | null)?.from;
    return <Navigate to={safeRedirectPath(from)} replace />;
  }
  return <Outlet />;
}

/** Signed-in students without a profile are sent to onboarding first. */
export function RequireProfile() {
  const me = useMe();
  if (me.isPending) return <FullPageLoading label="Loading your account" />;
  if (me.isError) {
    return (
      <div className="mx-auto max-w-xl p-8">
        <ErrorState
          title="Could not load your account"
          error={me.error}
          onRetry={() => void me.refetch()}
        />
      </div>
    );
  }
  if (me.data.profile === null) return <Navigate to="/onboarding" replace />;
  return <Outlet />;
}

/** Onboarding is only for students who have no profile yet. */
export function OnboardingOnly() {
  const me = useMe();
  if (me.isPending) return <FullPageLoading label="Loading your account" />;
  if (me.isError) {
    return (
      <div className="mx-auto max-w-xl p-8">
        <ErrorState
          title="Could not load your account"
          error={me.error}
          onRetry={() => void me.refetch()}
        />
      </div>
    );
  }
  if (me.data.profile !== null) return <Navigate to="/dashboard" replace />;
  return <Outlet />;
}
