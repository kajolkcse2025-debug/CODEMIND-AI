
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  listProblems,
  type CodingProblem,
} from "@/lib/api/problems";

export function CodingCoachPage() {
  const [problems, setProblems] = useState<CodingProblem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadProblems() {
      try {
        setLoading(true);
        setError(null);

        const response = await listProblems();

        if (!cancelled) {
          setProblems(response.items);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Unable to load coding problems.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadProblems();

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <main className="mx-auto w-full max-w-6xl space-y-6 p-6">
      <header className="space-y-2">
        <p className="text-sm font-medium text-primary">
          CODEMIND AI · MENTOR
        </p>

        <h1 className="text-3xl font-bold tracking-tight">
          Coding Coach
        </h1>

        <p className="text-muted-foreground">
          Practice coding problems and strengthen your
          problem-solving skills.
        </p>
      </header>

      {loading && (
        <p role="status" className="text-muted-foreground">
          Loading coding problems...
        </p>
      )}

      {error && !loading && (
        <section
          role="alert"
          className="space-y-3 rounded-xl border border-destructive/30 p-5"
        >
          <h2 className="text-lg font-semibold">
            Couldn't load problems
          </h2>

          <p className="text-sm text-muted-foreground">
            {error}
          </p>

          <button
            type="button"
            onClick={() => window.location.reload()}
            className="rounded-lg border px-4 py-2 text-sm font-medium hover:bg-muted"
          >
            Try again
          </button>
        </section>
      )}

      {!loading && !error && problems.length === 0 && (
        <section className="rounded-xl border p-8 text-center">
          <h2 className="text-lg font-semibold">
            No problems available yet
          </h2>

          <p className="mt-2 text-sm text-muted-foreground">
            Coding problems will appear here when they are
            available from the backend.
          </p>
        </section>
      )}

      {!loading && !error && problems.length > 0 && (
        <>
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">
              Practice problems
            </h2>

            <span className="text-sm text-muted-foreground">
              {problems.length} problems
            </span>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {problems.map((problem) => (
              <Link
                key={problem.id}
                to={`/coding-coach/${encodeURIComponent(
                  problem.slug,
                )}`}
                className="block rounded-xl border p-5 transition-colors hover:bg-muted/30"
              >
                <div className="flex items-start justify-between gap-3">
                  <h3 className="font-semibold">
                    {problem.title}
                  </h3>

                  <span className="shrink-0 rounded-full border px-3 py-1 text-xs capitalize">
                    {problem.difficulty}
                  </span>
                </div>

                <p className="mt-3 text-sm leading-6 text-muted-foreground">
                  {problem.description}
                </p>

                <span className="mt-4 inline-block text-sm font-medium text-primary">
                  Solve problem →
                </span>
              </Link>
            ))}
          </div>
        </>
      )}
    </main>
  );
}
