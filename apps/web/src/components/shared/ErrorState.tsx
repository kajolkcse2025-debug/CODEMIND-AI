import { TriangleAlert } from "lucide-react";

import { Button } from "@/components/ui/button";
import { describeError, isApiError } from "@/lib/api/errors";
import { cn } from "@/lib/utils";

interface ErrorStateProps {
  title?: string;
  error?: unknown;
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorState({
  title = "Something went wrong",
  error,
  message,
  onRetry,
  className,
}: ErrorStateProps) {
  const requestId = isApiError(error) ? error.requestId : null;
  return (
    <div
      role="alert"
      className={cn(
        "flex flex-col items-center justify-center rounded-lg border border-danger/40 bg-danger/5 px-6 py-10 text-center",
        className,
      )}
    >
      <TriangleAlert className="mb-3 size-7 text-danger" aria-hidden="true" />
      <h2 className="text-base font-semibold">{title}</h2>
      <p className="mt-2 max-w-md text-sm text-muted-foreground">
        {message ?? describeError(error)}
      </p>
      {requestId ? (
        <p className="mt-3 font-mono text-xs text-muted-foreground">Reference: {requestId}</p>
      ) : null}
      {onRetry ? (
        <Button variant="outline" size="sm" className="mt-5" onClick={onRetry}>
          Try again
        </Button>
      ) : null}
    </div>
  );
}
