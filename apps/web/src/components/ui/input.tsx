import type { InputHTMLAttributes, Ref } from "react";

import { cn } from "@/lib/utils";

export const fieldClasses =
  "w-full rounded-md border border-input bg-transparent px-3 text-sm placeholder:text-muted-foreground/70 disabled:cursor-not-allowed disabled:opacity-50 aria-[invalid=true]:border-danger";

export function Input({
  className,
  ref,
  ...props
}: InputHTMLAttributes<HTMLInputElement> & { ref?: Ref<HTMLInputElement> }) {
  return <input ref={ref} className={cn(fieldClasses, "h-9", className)} {...props} />;
}
