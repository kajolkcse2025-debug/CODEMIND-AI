
import { useNavigate } from "react-router-dom";

import { ErrorState } from "@/components/shared/ErrorState";
import { LoadingSkeleton } from "@/components/shared/LoadingSkeleton";
import { PageHeader } from "@/components/shared/PageHeader";
import {
  useCompleteRoadmapItem,
  useRoadmap,
} from "@/features/roadmap/hooks";

export function RoadmapPage() {
  const roadmap = useRoadmap();
  const complete = useCompleteRoadmapItem();
  const navigate = useNavigate();

  if (roadmap.isPending) {
    return (
      <>
        <PageHeader
          eyebrow="Your learning journey"
          title="DSA Roadmap"
          description="Your personalized DSA learning path."
        />
        <LoadingSkeleton variant="card" label="Building your roadmap" />
      </>
    );
  }

  if (roadmap.isError) {
    return (
      <>
        <PageHeader
          eyebrow="Your learning journey"
          title="DSA Roadmap"
          description="Your personalized DSA learning path."
        />
        <ErrorState
          title="Could not load your roadmap"
          error={roadmap.error}
          onRetry={() => void roadmap.refetch()}
        />
      </>
    );
  }

  const data = roadmap.data;
  const activeTopic = data.items.find((item) => item.status === "active");

  const formatDate = (date: string | null) => {
    if (!date) return "Not scheduled";

    return new Date(`${date}T00:00:00`).toLocaleDateString("en-IN", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  };

  const getTopicSlug = (title: string) =>
    title.toLowerCase().trim().replace(/\s+/g, "-");

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Your learning journey"
        title="DSA Roadmap"
        description="Learn, practice, complete topics and track your progress."
      />

      {complete.isSuccess && (
        <p role="status" className="rounded-lg bg-success/10 p-3 text-sm text-success">
          Topic completed successfully!
        </p>
      )}

      {complete.isError && (
        <p role="alert" className="rounded-lg bg-destructive/10 p-3 text-sm text-destructive">
          Could not complete the topic. Please try again.
        </p>
      )}

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Overall progress" value={`${data.progress_percentage}%`} />
        <StatCard label="Topics completed" value={`${data.completed_topics}/${data.total_topics}`} />
        <StatCard label="Daily study time" value={`${data.daily_minutes} min`} />
        <StatCard label="Total topics" value={String(data.total_topics)} />
      </section>

      <section className="rounded-2xl border border-border bg-card p-5">
        <div className="mb-3 flex justify-between">
          <h2 className="font-semibold">Your overall progress</h2>
          <span className="text-sm">{data.progress_percentage}%</span>
        </div>

        <div
          className="h-3 overflow-hidden rounded-full bg-muted"
          role="progressbar"
          aria-label="Roadmap progress"
          aria-valuenow={data.progress_percentage}
          aria-valuemin={0}
          aria-valuemax={100}
        >
          <div
            className="h-full rounded-full bg-primary transition-all"
            style={{ width: `${data.progress_percentage}%` }}
          />
        </div>
      </section>

      <section className="rounded-2xl border border-primary/30 bg-card p-5">
        <p className="text-xs font-semibold uppercase tracking-wider text-primary">
          Your next focus
        </p>

        {activeTopic ? (
          <>
            <h2 className="mt-2 text-2xl font-bold">{activeTopic.title}</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              {activeTopic.reason.explanation}
            </p>
            <button
              type="button"
              onClick={() => navigate(`/learn/${getTopicSlug(activeTopic.title)}`)}
              className="mt-4 rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground"
            >
              Learn {activeTopic.title} →
            </button>
          </>
        ) : (
          <p className="mt-2 text-sm text-muted-foreground">
            No active topics. Your roadmap may be complete!
          </p>
        )}
      </section>

      <section className="space-y-4">
        <div>
          <h2 className="text-xl font-bold">Your learning path</h2>
          <p className="text-sm text-muted-foreground">
            Open your active topic to learn. Complete it to unlock the next one.
          </p>
        </div>

        <div className="space-y-3">
          {data.items.map((item) => (
            <article
              key={item.id}
              className={`rounded-xl border bg-card p-4 ${
                item.status === "active" ? "border-primary" : "border-border"
              }`}
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="flex items-start gap-3">
                  <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-muted text-sm font-semibold">
                    {item.position}
                  </span>

                  <div>
                    <h3 className="font-semibold">{item.title}</h3>
                    <p className="mt-1 text-xs capitalize text-muted-foreground">
                      {item.phase} · {item.type}
                    </p>
                  </div>
                </div>

                <StatusBadge status={item.status} />
              </div>

              <p className="mt-3 text-sm text-muted-foreground">
                {item.reason.explanation}
              </p>

              <div className="mt-3 flex flex-wrap gap-x-5 gap-y-2 text-xs text-muted-foreground">
                <span>
                  Problems: {item.completed_problems}/{item.target_problems}
                </span>
                <span>Attempts: {item.reason.attempts}</span>
                {item.reason.attempts > 0 && (
                  <span>Mastery: {Math.round(item.reason.mastery)}%</span>
                )}
                <span>Due: {formatDate(item.due_date)}</span>
              </div>

              {item.status === "active" && (
                <div className="mt-4 flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={() => navigate(`/learn/${getTopicSlug(item.title)}`)}
                    className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground"
                  >
                    Learn Topic →
                  </button>

                  <button
                    type="button"
                    disabled={complete.isPending}
                    onClick={() => complete.mutate(item.id)}
                    className="rounded-lg border border-border px-4 py-2 text-sm font-semibold hover:bg-muted disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {complete.isPending ? "Saving..." : "Mark as Completed"}
                  </button>
                </div>
              )}

              {item.status === "done" && (
                <p className="mt-4 text-sm font-medium text-success">
                  ✓ Completed
                </p>
              )}
            </article>
          ))}
        </div>
      </section>

      <section className="rounded-xl border border-border bg-card p-5">
        <h2 className="font-semibold">Why this roadmap?</h2>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">
          {data.rationale}
        </p>
      </section>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="mt-2 text-2xl font-bold">{value}</p>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    active: "bg-primary/10 text-primary",
    done: "bg-success/10 text-success",
    upcoming: "bg-muted text-muted-foreground",
    skipped: "bg-muted text-muted-foreground",
  };

  return (
    <span
      className={`rounded-full px-3 py-1 text-xs font-medium capitalize ${
        styles[status] ?? "bg-muted text-muted-foreground"
      }`}
    >
      {status}
    </span>
  );
}
