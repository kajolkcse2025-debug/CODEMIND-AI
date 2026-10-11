import { useRouteError } from "react-router-dom";

import { ErrorState } from "@/components/shared/ErrorState";

/** Last-resort boundary for rendering errors, so a bug never shows a blank page. */
export function RouteError() {
  const error = useRouteError();
  if (import.meta.env.DEV) console.error(error);
  return (
    <div className="mx-auto max-w-xl p-8">
      <ErrorState
        title="This page crashed"
        message="Something broke while showing this page. Reloading usually fixes it."
        onRetry={() => window.location.reload()}
      />
    </div>
  );
}
