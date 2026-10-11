import type { Ref, SelectHTMLAttributes } from "react";

import { fieldClasses } from "@/components/ui/input";
import { cn } from "@/lib/utils";

/** Native <select>: fully accessible and mobile-friendly, styled like the other fields. */
export function Select({
  className,
  ref,
  ...props
}: SelectHTMLAttributes<HTMLSelectElement> & { ref?: Ref<HTMLSelectElement> }) {
  return (
    <select ref={ref} className={cn(fieldClasses, "h-9 bg-card pr-8", className)} {...props} />
  );
}
