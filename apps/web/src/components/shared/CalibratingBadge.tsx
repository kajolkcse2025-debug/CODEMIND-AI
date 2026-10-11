import { Gauge } from "lucide-react";

import { Badge } from "@/components/ui/badge";

interface CalibratingBadgeProps {
  /** For example "3 of 8 samples". Optional; never a score. */
  detail?: string;
}

/** Shown when there is not yet enough evidence for a trustworthy number. */
export function CalibratingBadge({ detail }: CalibratingBadgeProps) {
  return (
    <Badge variant="warning" title="Not enough evidence yet to show a reliable score.">
      <Gauge className="size-3" aria-hidden="true" />
      Calibrating{detail ? ` · ${detail}` : ""}
    </Badge>
  );
}
