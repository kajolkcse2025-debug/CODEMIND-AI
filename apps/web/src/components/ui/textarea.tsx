import type { Ref, TextareaHTMLAttributes } from "react";

import { fieldClasses } from "@/components/ui/input";
import { cn } from "@/lib/utils";

export function Textarea({
  className,
  ref,
  ...props
}: TextareaHTMLAttributes<HTMLTextAreaElement> & { ref?: Ref<HTMLTextAreaElement> }) {
  return <textarea ref={ref} className={cn(fieldClasses, "min-h-20 py-2", className)} {...props} />;
}
