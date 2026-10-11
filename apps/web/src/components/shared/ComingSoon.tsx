import { Hourglass } from "lucide-react";

import { PageHeader } from "@/components/shared/PageHeader";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

interface ComingSoonProps {
  eyebrow: string;
  title: string;
  description: string;
  /** What will live here. Plain descriptions, never sample data. */
  willInclude: string[];
}

/** Honest placeholder for modules that are not built yet. Shows no scores or statistics. */
export function ComingSoon({ eyebrow, title, description, willInclude }: ComingSoonProps) {
  return (
    <>
      <PageHeader eyebrow={eyebrow} title={title} description={description} />
      <Card className="max-w-2xl p-6">
        <div className="flex items-center gap-3">
          <Hourglass className="size-5 text-muted-foreground" aria-hidden="true" />
          <h2 className="font-display text-lg font-semibold">Coming soon</h2>
          <Badge variant="outline">Not built yet</Badge>
        </div>
        <p className="mt-3 text-sm text-muted-foreground">
          This part of CodeMind is planned for a later release. Nothing here is measured yet, so no
          numbers are shown.
        </p>
        <ul className="mt-5 space-y-2 text-sm">
          {willInclude.map((item) => (
            <li key={item} className="flex gap-3">
              <span
                className="mt-2 size-1 shrink-0 rounded-full bg-muted-foreground"
                aria-hidden="true"
              />
              {item}
            </li>
          ))}
        </ul>
      </Card>
    </>
  );
}
