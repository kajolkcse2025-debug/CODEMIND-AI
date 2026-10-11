import type { ReactNode } from "react";

import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface StatCardProps {
  label: string;
  /** ``null`` renders "Not measured yet". Never pass a placeholder number. */
  value: ReactNode | null;
  hint?: string;
  badge?: ReactNode;
  className?: string;
}

export function StatCard({ label, value, hint, badge, className }: StatCardProps) {
  const measured = value !== null && value !== undefined;
  return (
    <Card className={cn("p-5", className)}>
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm text-muted-foreground">{label}</p>
        {badge}
      </div>
      <p
        className={cn(
          "mt-3",
          measured
            ? "font-mono text-3xl font-medium tabular-nums"
            : "text-sm text-muted-foreground",
        )}
      >
        {measured ? value : "Not measured yet"}
      </p>
      {hint ? <p className="mt-2 text-xs text-muted-foreground">{hint}</p> : null}
    </Card>
  );
}
