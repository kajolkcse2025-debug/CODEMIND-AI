import { ShieldAlert } from "lucide-react";

import { Badge } from "@/components/ui/badge";

/** Marks anything not confirmed by a real code runner. Unverified results never affect scores. */
export function UnverifiedBadge() {
  return (
    <Badge
      variant="outline"
      title="This was not checked by a code runner, so it does not affect your scores or XP."
    >
      <ShieldAlert className="size-3" aria-hidden="true" />
      Unverified
    </Badge>
  );
}
