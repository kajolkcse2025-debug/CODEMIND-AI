import { cn } from "@/lib/utils";

export function BrandMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={cn("size-7", className)} aria-hidden="true">
      <path
        d="M12 9c-3 0-3 2-3 4s0 3-2 3c2 0 2 1 2 3s0 4 3 4M20 9c3 0 3 2 3 4s0 3 2 3c-2 0-2 1-2 3s0 4-3 4"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        className="text-primary"
      />
      <circle cx="16" cy="16" r="2" className="fill-primary" />
    </svg>
  );
}

export function Wordmark({ className }: { className?: string }) {
  return (
    <span className={cn("flex items-center gap-2", className)}>
      <BrandMark />
      <span className="font-display text-lg font-semibold tracking-tight">CodeMind</span>
    </span>
  );
}
