
import { useMemo, useState } from "react";
import {
  clearAssessmentHistory,
  getAssessmentAnalytics,
  getAssessmentHistory,
  type AssessmentHistoryEntry,
} from "./assessmentHistory";

function formatDate(value: string) {
  return new Date(value).toLocaleString(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function formatDuration(seconds: number) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}m ${remainingSeconds}s`;
}

function StatCard({
  label,
  value,
  detail,
}: {
  label: string;
  value: string | number;
  detail: string;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-3 text-3xl font-bold text-white">{value}</p>
      <p className="mt-2 text-xs text-slate-500">{detail}</p>
    </div>
  );
}

function TopicBar({
  topic,
  accuracy,
}: {
  topic: string;
  accuracy: number;
}) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between gap-3 text-sm">
        <span className="capitalize text-slate-300">
          {topic.replaceAll("-", " ")}
        </span>
        <span className="font-semibold text-white">{accuracy}%</span>
      </div>

      <div className="h-2.5 overflow-hidden rounded-full bg-white/10">
        <div
          className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-violet-500 transition-all"
          style={{ width: `${Math.min(100, Math.max(0, accuracy))}%` }}
        />
      </div>
    </div>
  );
}

function ScoreBadge({ score }: { score: number }) {
  const tone =
    score >= 80
      ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-300"
      : score >= 50
        ? "border-amber-400/20 bg-amber-400/10 text-amber-300"
        : "border-rose-400/20 bg-rose-400/10 text-rose-300";

  return (
    <span className={`rounded-full border px-3 py-1 text-sm font-semibold ${tone}`}>
      {score}%
    </span>
  );
}

export default function AssessmentHistoryPage() {
  const [history, setHistory] = useState<AssessmentHistoryEntry[]>(
    () => getAssessmentHistory(),
  );

  const analytics = useMemo(() => getAssessmentAnalytics(), [history]);

  function handleClearHistory() {
    const confirmed = window.confirm(
      "Are you sure you want to delete all assessment history from this browser?",
    );

    if (!confirmed) return;

    clearAssessmentHistory();
    setHistory([]);
  }

  const hasHistory = history.length > 0;

  return (
    <main className="min-h-screen bg-[#080b16] px-4 py-8 text-white sm:px-6 lg:px-10">
      <div className="mx-auto max-w-7xl space-y-8">
        <header className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.25em] text-cyan-400">
              CodeMind AI / Analytics
            </p>
            <h1 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
              Your assessment journey
            </h1>
            <p className="mt-3 max-w-2xl text-slate-400">
              Review your previous assessments, understand your topic-wise
              performance, and identify what to practise next.
            </p>
          </div>

          {hasHistory && (
            <button
              type="button"
              onClick={handleClearHistory}
              className="rounded-xl border border-rose-400/20 px-4 py-2.5 text-sm text-rose-300 transition hover:bg-rose-400/10"
            >
              Clear history
            </button>
          )}
        </header>

        {!hasHistory ? (
          <section className="rounded-3xl border border-white/10 bg-white/[0.04] px-6 py-16 text-center">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-cyan-400/10 text-3xl">
              ◈
            </div>
            <h2 className="mt-6 text-2xl font-bold">
              Your journey starts here
            </h2>
            <p className="mx-auto mt-3 max-w-lg text-sm leading-6 text-slate-400">
              You haven't completed an assessment yet. Complete your first
              assessment to see your scores, topic strengths, improvement
              trends, and learning recommendations here.
            </p>
            <p className="mt-6 text-xs text-slate-500">
              Your completed assessments will appear on this page.
            </p>
          </section>
        ) : (
          <>
            <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <StatCard
                label="Assessments completed"
                value={analytics.completed}
                detail="Completed assessment sessions"
              />
              <StatCard
                label="Average score"
                value={`${analytics.averageScore}%`}
                detail="Average across saved assessments"
              />
              <StatCard
                label="Overall accuracy"
                value={`${analytics.overallAccuracy}%`}
                detail={`${analytics.totalCorrect} correct out of ${analytics.totalQuestions}`}
              />
              <StatCard
                label="Questions attempted"
                value={analytics.totalQuestions}
                detail="Across your saved assessments"
              />
            </section>

            <section className="grid gap-6 lg:grid-cols-2">
              <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-6">
                <h2 className="text-lg font-bold">Topic performance</h2>
                <p className="mt-1 text-sm text-slate-400">
                  Accuracy calculated from your saved assessment answers.
                </p>

                {analytics.topics.length === 0 ? (
                  <p className="mt-8 text-sm text-slate-500">
                    Topic-level results aren't available yet.
                  </p>
                ) : (
                  <div className="mt-7 space-y-6">
                    {analytics.topics.map((topic) => (
                      <TopicBar
                        key={topic.topic}
                        topic={topic.topic}
                        accuracy={topic.accuracy}
                      />
                    ))}
                  </div>
                )}
              </div>

              <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-6">
                <h2 className="text-lg font-bold">Your learning insights</h2>
                <p className="mt-1 text-sm text-slate-400">
                  Based on your recorded assessment performance.
                </p>

                <div className="mt-6 space-y-4">
                  <div className="rounded-xl border border-emerald-400/10 bg-emerald-400/[0.06] p-4">
                    <p className="text-xs font-semibold uppercase tracking-wider text-emerald-300">
                      Strongest observed topic
                    </p>
                    <p className="mt-2 text-xl font-bold capitalize">
                      {analytics.strongestTopic
                        ? analytics.strongestTopic.topic.replaceAll("-", " ")
                        : "Not enough data"}
                    </p>
                    {analytics.strongestTopic && (
                      <p className="mt-1 text-sm text-slate-400">
                        {analytics.strongestTopic.accuracy}% accuracy
                      </p>
                    )}
                  </div>

                  <div className="rounded-xl border border-amber-400/10 bg-amber-400/[0.06] p-4">
                    <p className="text-xs font-semibold uppercase tracking-wider text-amber-300">
                      Topic to practise next
                    </p>
                    <p className="mt-2 text-xl font-bold capitalize">
                      {analytics.weakestTopic
                        ? analytics.weakestTopic.topic.replaceAll("-", " ")
                        : "Not enough data"}
                    </p>
                    {analytics.weakestTopic && (
                      <p className="mt-1 text-sm text-slate-400">
                        {analytics.weakestTopic.accuracy}% accuracy — consider
                        revising this topic.
                      </p>
                    )}
                  </div>

                  <p className="rounded-xl border border-white/10 bg-white/[0.03] p-4 text-sm leading-6 text-slate-400">
                    These insights describe your recorded answers. They are
                    not proof of coding mastery or interview readiness.
                  </p>
                </div>
              </div>
            </section>

            <section className="overflow-hidden rounded-2xl border border-white/10 bg-white/[0.04]">
              <div className="flex flex-col justify-between gap-2 border-b border-white/10 p-6 sm:flex-row sm:items-center">
                <div>
                  <h2 className="text-lg font-bold">Assessment history</h2>
                  <p className="mt-1 text-sm text-slate-400">
                    Your most recent completed assessments.
                  </p>
                </div>
                <span className="text-xs text-slate-500">
                  Showing latest {analytics.recentAttempts.length}
                </span>
              </div>

              <div className="divide-y divide-white/10">
                {analytics.recentAttempts.map((attempt) => (
                  <div
                    key={attempt.id}
                    className="flex flex-col justify-between gap-4 p-5 sm:flex-row sm:items-center"
                  >
                    <div>
                      <p className="font-semibold">DSA Assessment</p>
                      <p className="mt-1 text-sm text-slate-400">
                        {formatDate(attempt.completedAt)}
                      </p>
                      <p className="mt-1 text-xs text-slate-500">
                        {attempt.correctAnswers} of {attempt.totalQuestions}{" "}
                        correct · {formatDuration(attempt.durationSeconds)}
                      </p>
                    </div>
                    <ScoreBadge score={attempt.score} />
                  </div>
                ))}
              </div>
            </section>
          </>
        )}

        <footer className="text-center text-xs text-slate-600">
          CodeMind AI · Learn from every attempt. Improve with every session.
        </footer>
      </div>
    </main>
  );
}
