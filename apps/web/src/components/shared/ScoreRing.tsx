import { cn } from "@/lib/utils";

interface ScoreRingProps {
  /** ``null`` means "not measured": a dashed, empty ring and no number. */
  value: number | null;
  max?: number;
  label: string;
  size?: number;
  className?: string;
}

const STROKE = 8;

export function ScoreRing({ value, max = 100, label, size = 112, className }: ScoreRingProps) {
  const radius = (size - STROKE) / 2;
  const circumference = 2 * Math.PI * radius;
  const measured = value !== null && Number.isFinite(value);
  const fraction = measured ? Math.min(Math.max(value / max, 0), 1) : 0;

  return (
    <figure
      className={cn("inline-flex flex-col items-center gap-2", className)}
      aria-label={
        measured ? `${label}: ${Math.round(value)} out of ${max}` : `${label}: not measured yet`
      }
    >
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90" aria-hidden="true">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            strokeWidth={STROKE}
            className="stroke-muted"
            strokeDasharray={measured ? undefined : "3 6"}
          />
          {measured ? (
            <circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="none"
              strokeWidth={STROKE}
              strokeLinecap="round"
              className="stroke-primary transition-[stroke-dashoffset] duration-700"
              strokeDasharray={circumference}
              strokeDashoffset={circumference * (1 - fraction)}
            />
          ) : null}
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          {measured ? (
            <span className="font-mono text-2xl font-medium tabular-nums">{Math.round(value)}</span>
          ) : (
            <span className="px-3 text-center text-xs leading-tight text-muted-foreground">
              Not measured
            </span>
          )}
        </div>
      </div>
      <figcaption className="text-xs text-muted-foreground">{label}</figcaption>
    </figure>
  );
}
