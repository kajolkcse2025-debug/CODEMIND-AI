
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import {
  getProblem,
  submitCode,
  type ProblemDetail,
  type SubmissionResult,
  type SubmitCode,
} from "@/lib/api/problems";

type Language = SubmitCode["language"];

const starterCode: Record<Language, string> = {
  python: `# Write your Python solution here
`,
  java: `import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        // Write your solution here

        sc.close();
    }
}
`,
  cpp: `#include <iostream>
using namespace std;

int main() {
    // Write your solution here

    return 0;
}
`,
};

const verdictLabels: Record<SubmissionResult["verdict"], string> = {
  accepted: "Accepted",
  wrong_answer: "Wrong Answer",
  runtime_error: "Runtime Error",
  time_limit: "Time Limit Exceeded",
  memory_limit: "Memory Limit Exceeded",
  compile_error: "Compilation Error",
  runner_unavailable: "Code runner unavailable",
};

export function CodingProblemPage() {
  const { slug } = useParams<{ slug: string }>();

  const [problem, setProblem] = useState<ProblemDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [language, setLanguage] = useState<Language>("python");
  const [sourceCode, setSourceCode] = useState(starterCode.python);
  const [submission, setSubmission] = useState<SubmissionResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadProblem() {
      if (!slug) {
        setError("Problem not found.");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        setProblem(null);

        const result = await getProblem(slug);

        if (!cancelled) {
          setProblem(result);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Unable to load this problem.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadProblem();

    return () => {
      cancelled = true;
    };
  }, [slug]);

  function handleLanguageChange(nextLanguage: Language) {
    setLanguage(nextLanguage);
    setSourceCode(starterCode[nextLanguage]);
    setSubmission(null);
    setSubmitError(null);
  }

  async function handleSubmit() {
    if (!slug || !sourceCode.trim()) {
      setSubmitError("Please write some code before submitting.");
      return;
    }

    try {
      setSubmitting(true);
      setSubmitError(null);
      setSubmission(null);

      const result = await submitCode(slug, {
        language,
        source_code: sourceCode,
      });

      setSubmission(result);
    } catch (err) {
      setSubmitError(
        err instanceof Error
          ? err.message
          : "Unable to submit your code. Please try again.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <main className="mx-auto w-full max-w-5xl p-6">
        <p className="text-sm text-muted-foreground">
          Loading problem...
        </p>
      </main>
    );
  }

  if (error || !problem) {
    return (
      <main className="mx-auto w-full max-w-5xl space-y-4 p-6">
        <Link
          to="/coding-coach"
          className="text-sm text-primary hover:underline"
        >
          &larr; Back to Coding Coach
        </Link>

        <p role="alert" className="text-sm text-red-500">
          {error ?? "Problem not found."}
        </p>
      </main>
    );
  }

  return (
    <main className="mx-auto w-full max-w-6xl space-y-6 p-6">
      <Link
        to="/coding-coach"
        className="inline-block text-sm text-primary hover:underline"
      >
        &larr; Back to Coding Coach
      </Link>

      <section className="rounded-xl border p-5">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
          <h1 className="text-2xl font-bold">{problem.title}</h1>

          <span
            className={`rounded-full px-3 py-1 text-sm font-medium capitalize ${
              problem.difficulty === "easy"
                ? "bg-green-100 text-green-800"
                : problem.difficulty === "medium"
                  ? "bg-yellow-100 text-yellow-800"
                  : "bg-red-100 text-red-800"
            }`}
          >
            {problem.difficulty}
          </span>
        </div>

        <div className="whitespace-pre-wrap text-sm leading-7">
          {problem.description}
        </div>

        {problem.input_format && (
          <div className="mt-5">
            <h2 className="mb-1 font-semibold">Input Format</h2>
            <p className="whitespace-pre-wrap text-sm leading-6">
              {problem.input_format}
            </p>
          </div>
        )}

        {problem.output_format && (
          <div className="mt-4">
            <h2 className="mb-1 font-semibold">Output Format</h2>
            <p className="whitespace-pre-wrap text-sm leading-6">
              {problem.output_format}
            </p>
          </div>
        )}

        {problem.constraints && problem.constraints.length > 0 && (
          <div className="mt-4">
            <h2 className="mb-2 font-semibold">Constraints</h2>
            <ul className="list-disc space-y-1 pl-5 text-sm">
              {problem.constraints.map((constraint, index) => (
                <li key={`${index}-${constraint}`}>{constraint}</li>
              ))}
            </ul>
          </div>
        )}

        {problem.examples && problem.examples.length > 0 && (
          <div className="mt-5 space-y-4">
            <h2 className="font-semibold">Examples</h2>

            {problem.examples.map((example, index) => (
              <div
                key={index}
                className="space-y-2 rounded-lg bg-muted/50 p-3"
              >
                <p className="text-sm font-medium">Example {index + 1}</p>

                <div>
                  <p className="text-xs font-semibold text-muted-foreground">
                    Input
                  </p>
                  <pre className="overflow-x-auto whitespace-pre-wrap text-sm">
                    {example.input}
                  </pre>
                </div>

                <div>
                  <p className="text-xs font-semibold text-muted-foreground">
                    Output
                  </p>
                  <pre className="overflow-x-auto whitespace-pre-wrap text-sm">
                    {example.output}
                  </pre>
                </div>

                {example.explanation && (
                  <p className="text-sm">
                    <span className="font-semibold">Explanation: </span>
                    {example.explanation}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="space-y-4 rounded-xl border p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-xl font-bold">Your Solution</h2>

          <label className="flex items-center gap-2 text-sm">
            <span>Language</span>
            <select
              value={language}
              onChange={(event) =>
                handleLanguageChange(event.target.value as Language)
              }
              disabled={submitting}
              className="rounded-md border bg-background px-3 py-2"
            >
              <option value="python">Python</option>
              <option value="java">Java</option>
              <option value="cpp">C++</option>
            </select>
          </label>
        </div>

        <textarea
          value={sourceCode}
          onChange={(event) => setSourceCode(event.target.value)}
          disabled={submitting}
          spellCheck={false}
          aria-label="Code editor"
          placeholder="Write your solution here..."
          className="min-h-[320px] w-full resize-y rounded-lg border bg-slate-950 p-4 font-mono text-sm leading-6 text-green-300 outline-none focus:ring-2 focus:ring-primary"
        />

        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-xs text-muted-foreground">
            Your code will be checked against the problem's test cases.
          </p>

          <button
            type="button"
            onClick={handleSubmit}
            disabled={submitting || !sourceCode.trim()}
            className="rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {submitting ? "Running..." : "Run & Submit"}
          </button>
        </div>

        {submitError && (
          <div
            role="alert"
            className="rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-700"
          >
            {submitError}
          </div>
        )}

        {submission && (
          <div
            aria-live="polite"
            className={`space-y-2 rounded-lg border p-4 ${
              submission.verdict === "accepted"
                ? "border-green-300 bg-green-50 text-green-900"
                : "border-red-300 bg-red-50 text-red-900"
            }`}
          >
            <h3 className="text-lg font-bold">
              {verdictLabels[submission.verdict]}
            </h3>

            <p className="text-sm">
              Tests passed: {submission.tests_passed} /{" "}
              {submission.tests_total}
            </p>

            <p className="text-sm">
              Verification: {submission.verified ? "Verified" : "Unverified"}
            </p>

            {submission.detail && (
              <p className="whitespace-pre-wrap break-words text-sm">
                {submission.detail}
              </p>
            )}
          </div>
        )}
      </section>
    </main>
  );
}
