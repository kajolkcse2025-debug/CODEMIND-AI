import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

interface LoadingSkeletonProps {
  variant?: "page" | "card" | "lines";
  lines?: number;
  label?: string;
  className?: string;
}

/** Announces itself to assistive tech and never shows invented numbers. */
export function LoadingSkeleton({
  variant = "lines",
  lines = 3,
  label = "Loading",
  className,
}: LoadingSkeletonProps) {
  return (
    <div role="status" aria-busy="true" aria-live="polite" className={cn("w-full", className)}>
      <span className="sr-only">{label}…</span>
      {variant === "page" ? (
        <div className="space-y-6">
          <div className="space-y-3">
            <Skeleton className="h-3 w-24" />
            <Skeleton className="h-8 w-64" />
            <Skeleton className="h-4 w-96 max-w-full" />
          </div>
          <Skeleton className="h-48 w-full" />
          <div className="grid gap-4 sm:grid-cols-2">
            <Skeleton className="h-32" />
            <Skeleton className="h-32" />
          </div>
        </div>
      ) : variant === "card" ? (
        <Skeleton className="h-40 w-full" />
      ) : (
        <div className="space-y-3">
          {Array.from({ length: lines }, (_, index) => (
            <Skeleton key={index} className={cn("h-4", index === lines - 1 ? "w-2/3" : "w-full")} />
          ))}
        </div>
      )}
    </div>
  );
}
