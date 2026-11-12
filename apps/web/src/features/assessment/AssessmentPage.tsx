
import { useEffect, useRef, useState } from "react";
import Editor from "@monaco-editor/react";
import {
  AlertCircle,
  BookOpen,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Code2,
  Flag,
  Loader2,
  Play,
  RotateCcw,
  Terminal,
  BarChart3,
  Clock,
  Trophy,
} from "lucide-react";

import {
  getAssessmentQuestions,
  submitAssessmentCode,
  type AssessmentQuestion,
  type AssessmentSubmissionResult,
} from "@/lib/api/codingAssessment";

import { saveAssessmentResult } from "./assessmentHistory";

type AssessmentLanguage = "python" | "java" | "cpp";

const ASSESSMENT_DURATION = 30 * 60;

const starterCode: Record<AssessmentLanguage, string> = {
  python: `# Write your Python solution here
# Read input using input()
`,
  java: `import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        // Write your solution here

        sc.close();
    }
}`,
  cpp: `#include <iostream>
#include <vector>
#include <string>
using namespace std;

int main() {
    // Write your solution here

    return 0;
}`,
};

function getVerdict(result: AssessmentSubmissionResult | null): string {
  if (!result) return "";
  return result.verdict.replaceAll("_", " ");
}

function isAccepted(result: AssessmentSubmissionResult | null): boolean {
  return Boolean(
    result?.verified &&
      result.counts_toward_metrics &&
      result.verdict === "accepted",
  );
}

function formatTime(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const remaining = seconds % 60;

  return `${String(minutes).padStart(2, "0")}:${String(remaining).padStart(2, "0")}`;
}

export function AssessmentPage() {
  const [questions, setQuestions] = useState<AssessmentQuestion[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [language, setLanguage] = useState<AssessmentLanguage>("python");

  const [codeByQuestion, setCodeByQuestion] = useState<
    Record<string, string>
  >({});

  const [resultsByQuestion, setResultsByQuestion] = useState<
    Record<string, AssessmentSubmissionResult>
  >({});

  const [markedForReview, setMarkedForReview] = useState<string[]>([]);
  const [showSummary, setShowSummary] = useState(false);

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [runMessage, setRunMessage] = useState("");

  const [isFinished, setIsFinished] = useState(false);
  const [remainingSeconds, setRemainingSeconds] =
    useState(ASSESSMENT_DURATION);

  const startedAtRef = useRef(Date.now());
  const savedRef = useRef(false);

  useEffect(() => {
    let cancelled = false;

    async function loadQuestions() {
      setLoading(true);
      setError("");

      try {
        const response = await getAssessmentQuestions(8);

        if (!cancelled) {
          setQuestions(response.questions);
          startedAtRef.current = Date.now();
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Unable to load assessment questions.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadQuestions();

    return () => {
      cancelled = true;
    };
  }, []);

  const question = questions[currentIndex];

  const codeKey = question ? `${question.slug}:${language}` : "";

  const sourceCode = question
    ? codeByQuestion[codeKey] ??
      (language === "python"
        ? question.starter_code || starterCode.python
        : starterCode[language])
    : "";

  const currentResult = question
    ? resultsByQuestion[`${question.slug}:${language}`] ?? null
    : null;

  const verifiedQuestionSlugs = new Set(
    Object.values(resultsByQuestion)
      .filter((result) => result.verified)
      .map((result) => result.question_slug),
  );

  const acceptedQuestionSlugs = new Set(
    Object.values(resultsByQuestion)
      .filter(isAccepted)
      .map((result) => result.question_slug),
  );

  const verifiedResults = Object.values(resultsByQuestion).filter(
    (result) => result.verified,
  );

  const acceptedSubmissions = verifiedResults.filter(
    (result) =>
      result.counts_toward_metrics && result.verdict === "accepted",
  ).length;

  const totalTestsPassed = verifiedResults.reduce(
    (total, result) => total + result.tests_passed,
    0,
  );

  const totalTestsRun = verifiedResults.reduce(
    (total, result) => total + result.tests_total,
    0,
  );

  // Timer runs only after questions have loaded.
  useEffect(() => {
    if (loading || isFinished || questions.length === 0) return;

    const timer = window.setInterval(() => {
      setRemainingSeconds((previous) => Math.max(0, previous - 1));
    }, 1000);

    return () => window.clearInterval(timer);
  }, [loading, isFinished, questions.length]);

  function handleCodeChange(value: string) {
    if (!question || isFinished) return;

    setCodeByQuestion((previous) => ({
      ...previous,
      [`${question.slug}:${language}`]: value,
    }));

    setRunMessage("");
  }

  function handleLanguageChange(nextLanguage: AssessmentLanguage) {
    if (isFinished) return;

    setLanguage(nextLanguage);
    setRunMessage("");
    setError("");
  }

  function handleReset() {
    if (!question || isFinished || submitting) return;

    setCodeByQuestion((previous) => {
      const updated = { ...previous };
      delete updated[`${question.slug}:${language}`];
      return updated;
    });

    setResultsByQuestion((previous) => {
      const updated = { ...previous };
      delete updated[`${question.slug}:${language}`];
      return updated;
    });

    setRunMessage("");
    setError("");
  }

  async function handleSubmit() {
    if (!question || submitting || isFinished) return;

    setSubmitting(true);
    setError("");
    setRunMessage("Submitting your solution...");

    try {
      const result = await submitAssessmentCode(question.slug, {
        language,
        source_code: sourceCode,
      });

      setResultsByQuestion((previous) => ({
        ...previous,
        [`${question.slug}:${language}`]: result,
      }));

      setRunMessage("Submission completed.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Submission failed. Please try again.",
      );
      setRunMessage("");
    } finally {
      setSubmitting(false);
    }
  }

  function finishAssessment() {
    if (isFinished || submitting || questions.length === 0) return;

    const acceptedCount = questions.filter((item) =>
      acceptedQuestionSlugs.has(item.slug),
    ).length;

    const score = Math.round(
      (acceptedCount / questions.length) * 100,
    );

    const topicMap = new Map<
      string,
      { correct: number; total: number }
    >();

    for (const item of questions) {
      const current = topicMap.get(item.topic) ?? {
        correct: 0,
        total: 0,
      };

      current.total += 1;

      if (acceptedQuestionSlugs.has(item.slug)) {
        current.correct += 1;
      }

      topicMap.set(item.topic, current);
    }

    const topicScores = Array.from(topicMap.entries()).map(
      ([topic, values]) => ({
        topic,
        correct: values.correct,
        total: values.total,
      }),
    );

    const durationSeconds = Math.min(
      ASSESSMENT_DURATION,
      Math.max(
        0,
        Math.floor((Date.now() - startedAtRef.current) / 1000),
      ),
    );

    if (!savedRef.current) {
      try {
        saveAssessmentResult({
          score,
          totalQuestions: questions.length,
          correctAnswers: acceptedCount,
          durationSeconds,
          topicScores,
        });

        savedRef.current = true;
      } catch {
        setError(
          "Assessment finished, but history could not be saved in this browser.",
        );
      }
    }

    setIsFinished(true);
    setShowSummary(true);
    setRunMessage("");
  }

  // Automatically finish when the timer reaches zero.
  useEffect(() => {
    if (
      remainingSeconds === 0 &&
      !isFinished &&
      !submitting &&
      questions.length > 0
    ) {
      finishAssessment();
    }
  }, [remainingSeconds, isFinished, submitting, questions.length]);

  function goToQuestion(index: number) {
    if (
      index < 0 ||
      index >= questions.length ||
      isFinished
    ) {
      return;
    }

    setCurrentIndex(index);
    setRunMessage("");
    setError("");
  }

  function toggleReviewMark() {
    if (!question || isFinished) return;

    setMarkedForReview((previous) =>
      previous.includes(question.slug)
        ? previous.filter((slug) => slug !== question.slug)
        : [...previous, question.slug],
    );
  }

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="flex items-center gap-3 text-gray-500">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span>Loading assessment...</span>
        </div>
      </div>
    );
  }

  if (error && questions.length === 0) {
    return (
      <div className="mx-auto max-w-2xl p-8">
        <div className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-5 text-red-700">
          <AlertCircle className="mt-0.5 h-5 w-5 shrink-0" />
          <div>
            <h2 className="font-semibold">Unable to load assessment</h2>
            <p className="mt-1 text-sm">{error}</p>
            <button
              type="button"
              onClick={() => window.location.reload()}
              className="mt-3 rounded-lg border border-red-300 px-3 py-2 text-sm font-medium hover:bg-red-100"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (questions.length === 0 || !question) {
    return (
      <div className="p-8 text-center">
        <BookOpen className="mx-auto mb-3 h-8 w-8 text-gray-400" />
        <h2 className="text-xl font-semibold">
          No assessment question available
        </h2>
        <p className="mt-2 text-gray-500">
          Please refresh the page and try again.
        </p>
      </div>
    );
  }

  const examples = question.examples ?? [];
  const isMarked = markedForReview.includes(question.slug);

  return (
    <div className="mx-auto w-full max-w-[1600px] space-y-6 p-4 md:p-6">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Code2 className="h-4 w-4" />
            Coding assessment
          </div>

          <h1 className="mt-1 text-2xl font-bold tracking-tight text-gray-900">
            {isFinished ? "Assessment completed" : "Practice and improve"}
          </h1>

          <p className="mt-1 text-sm text-gray-500">
            {isFinished
              ? "Your assessment result has been saved to your history."
              : "Solve coding problems, submit solutions, and track your progress."}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm">
            <BookOpen className="h-4 w-4 text-gray-500" />
            Question {currentIndex + 1} of {questions.length}
          </div>

          <div
            className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-semibold ${
              remainingSeconds <= 300 && !isFinished
                ? "border-red-200 bg-red-50 text-red-700"
                : "border-gray-200 bg-white text-gray-700"
            }`}
          >
            <Clock className="h-4 w-4" />
            {isFinished ? "Finished" : formatTime(remainingSeconds)}
          </div>

          <button
            type="button"
            onClick={() => setShowSummary((previous) => !previous)}
            className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm font-medium hover:bg-gray-50"
          >
            <BarChart3 className="h-4 w-4" />
            {showSummary ? "Hide summary" : "View summary"}
          </button>

          {!isFinished && (
            <button
              type="button"
              onClick={finishAssessment}
              disabled={submitting}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              Finish assessment
            </button>
          )}
        </div>
      </header>

      {isFinished && (
        <section className="rounded-2xl border border-emerald-200 bg-emerald-50 p-6">
          <div className="flex items-center gap-3">
            <Trophy className="h-7 w-7 text-emerald-700" />
            <div>
              <h2 className="text-xl font-bold text-emerald-900">
                Assessment completed!
              </h2>
              <p className="mt-1 text-sm text-emerald-800">
                Your results have been saved in this browser.
              </p>
            </div>
          </div>

          <div className="mt-5 grid gap-3 sm:grid-cols-3">
            <div className="rounded-xl bg-white p-4">
              <p className="text-sm text-gray-500">Score</p>
              <p className="mt-1 text-3xl font-bold text-gray-900">
                {Math.round(
                  (acceptedQuestionSlugs.size / questions.length) * 100,
                )}
                %
              </p>
            </div>

            <div className="rounded-xl bg-white p-4">
              <p className="text-sm text-gray-500">Accepted questions</p>
              <p className="mt-1 text-3xl font-bold text-gray-900">
                {acceptedQuestionSlugs.size}/{questions.length}
              </p>
            </div>

            <div className="rounded-xl bg-white p-4">
              <p className="text-sm text-gray-500">Verified questions</p>
              <p className="mt-1 text-3xl font-bold text-gray-900">
                {verifiedQuestionSlugs.size}/{questions.length}
              </p>
            </div>
          </div>
        </section>
      )}

      <section className="rounded-xl border border-gray-200 bg-white p-4">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <div>
            <p className="text-sm font-semibold text-gray-800">
              Your progress
            </p>
            <p className="mt-1 text-xs text-gray-500">
              {verifiedQuestionSlugs.size} of {questions.length} questions have
              verified submissions
            </p>
          </div>

          <p className="text-sm font-semibold text-blue-700">
            {Math.round(
              (verifiedQuestionSlugs.size / questions.length) * 100,
            )}
            %
          </p>
        </div>

        <div className="h-2 overflow-hidden rounded-full bg-gray-100">
          <div
            className="h-full rounded-full bg-blue-600 transition-all"
            style={{
              width: `${(verifiedQuestionSlugs.size / questions.length) * 100}%`,
            }}
          />
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {questions.map((item, index) => {
            const isCurrent = index === currentIndex;
            const isVerified = verifiedQuestionSlugs.has(item.slug);
            const needsReview = markedForReview.includes(item.slug);

            return (
              <button
                key={item.slug}
                type="button"
                onClick={() => goToQuestion(index)}
                disabled={isFinished}
                className={`relative flex h-11 min-w-11 items-center justify-center rounded-lg border px-3 text-sm font-semibold transition ${
                  isCurrent
                    ? "border-blue-600 bg-blue-600 text-white"
                    : isVerified
                      ? "border-green-200 bg-green-50 text-green-700"
                      : "border-gray-200 bg-white text-gray-700"
                } disabled:cursor-default`}
                aria-label={`Go to question ${index + 1}: ${item.title}`}
              >
                {index + 1}

                {isVerified && (
                  <CheckCircle2
                    className={`absolute -right-1 -top-1 h-4 w-4 rounded-full ${
                      isCurrent
                        ? "bg-blue-600 text-white"
                        : "bg-white text-green-600"
                    }`}
                  />
                )}

                {needsReview && (
                  <Flag className="absolute -bottom-1 -right-1 h-3.5 w-3.5 fill-amber-400 text-amber-600" />
                )}
              </button>
            );
          })}
        </div>
      </section>

      {showSummary && (
        <section className="rounded-xl border border-gray-200 bg-white p-5">
          <h2 className="text-lg font-bold text-gray-900">
            Session summary
          </h2>

          <p className="mt-1 text-sm text-gray-500">
            Based on verified code submissions. An accepted solution is counted
            once per question.
          </p>

          <div className="mt-4 grid grid-cols-2 gap-3 lg:grid-cols-4">
            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-500">Total questions</p>
              <p className="mt-1 text-2xl font-bold">{questions.length}</p>
            </div>

            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-500">Questions attempted</p>
              <p className="mt-1 text-2xl font-bold">
                {verifiedQuestionSlugs.size}
              </p>
            </div>

            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-500">Accepted questions</p>
              <p className="mt-1 text-2xl font-bold">
                {acceptedQuestionSlugs.size}
              </p>
            </div>

            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-500">Marked for review</p>
              <p className="mt-1 text-2xl font-bold">
                {markedForReview.length}
              </p>
            </div>
          </div>

          <div className="mt-4 rounded-lg border border-gray-200 p-4">
            <p className="text-sm font-semibold text-gray-800">
              Verified submission details
            </p>

            <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-3">
              <div>
                <p className="text-xs text-gray-500">Accepted submissions</p>
                <p className="mt-1 text-lg font-semibold">
                  {acceptedSubmissions}
                </p>
              </div>

              <div>
                <p className="text-xs text-gray-500">Test cases passed</p>
                <p className="mt-1 text-lg font-semibold">
                  {totalTestsPassed} / {totalTestsRun}
                </p>
              </div>

              <div>
                <p className="text-xs text-gray-500">Verified submissions</p>
                <p className="mt-1 text-lg font-semibold">
                  {verifiedResults.length}
                </p>
              </div>
            </div>
          </div>
        </section>
      )}

      <div className="grid grid-cols-1 items-start gap-6 xl:grid-cols-2">
        <section className="min-w-0 overflow-hidden rounded-xl border border-gray-200 bg-white">
          <div className="border-b border-gray-200 p-5">
            <div className="flex flex-wrap items-center gap-2">
              <span
                className={`rounded-full px-2.5 py-1 text-xs font-semibold capitalize ${
                  question.difficulty === "easy"
                    ? "bg-green-100 text-green-700"
                    : question.difficulty === "medium"
                      ? "bg-yellow-100 text-yellow-800"
                      : "bg-red-100 text-red-700"
                }`}
              >
                {question.difficulty}
              </span>

              <span className="rounded-full bg-gray-100 px-2.5 py-1 text-xs text-gray-600">
                {question.topic}
              </span>

              {isMarked && (
                <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2.5 py-1 text-xs font-semibold text-amber-800">
                  <Flag className="h-3 w-3" />
                  Review
                </span>
              )}

              <span className="ml-auto text-xs text-gray-500">
                {question.time_limit_sec}s execution limit
              </span>
            </div>

            <h2 className="mt-4 text-xl font-bold text-gray-900">
              {question.title}
            </h2>
          </div>

          <div className="space-y-6 p-5">
            <section>
              <h3 className="mb-2 font-semibold text-gray-900">
                Problem statement
              </h3>

              <div className="whitespace-pre-wrap text-sm leading-7 text-gray-700">
                {question.statement}
              </div>
            </section>

            {examples.length > 0 && (
              <section>
                <h3 className="mb-3 font-semibold text-gray-900">
                  Examples
                </h3>

                <div className="space-y-3">
                  {examples.map((example, index) => (
                    <div
                      key={`${question.slug}-example-${index}`}
                      className="overflow-hidden rounded-lg border border-gray-200"
                    >
                      <div className="border-b bg-gray-50 px-3 py-2 text-xs font-semibold text-gray-600">
                        Example {index + 1}
                      </div>

                      <div className="space-y-3 p-3">
                        <div>
                          <p className="mb-1 text-xs font-medium text-gray-500">
                            Input
                          </p>
                          <pre className="overflow-x-auto whitespace-pre-wrap rounded-md bg-gray-50 p-3 font-mono text-sm">
                            {example.input || "(empty)"}
                          </pre>
                        </div>

                        <div>
                          <p className="mb-1 text-xs font-medium text-gray-500">
                            Output
                          </p>
                          <pre className="overflow-x-auto whitespace-pre-wrap rounded-md bg-gray-50 p-3 font-mono text-sm">
                            {example.output || "(empty)"}
                          </pre>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {question.constraints && (
              <section>
                <h3 className="mb-2 font-semibold text-gray-900">
                  Constraints
                </h3>
                <div className="whitespace-pre-wrap rounded-lg bg-gray-50 p-3 text-sm leading-6 text-gray-700">
                  {question.constraints}
                </div>
              </section>
            )}

            <section>
              <h3 className="mb-3 font-semibold text-gray-900">
                Target complexity
              </h3>

              <div className="grid gap-3 sm:grid-cols-2">
                <div className="rounded-lg border border-gray-200 p-3">
                  <p className="text-xs text-gray-500">Time complexity</p>
                  <p className="mt-1 font-mono text-sm">
                    {question.optimal_time_complexity || "Not specified"}
                  </p>
                </div>

                <div className="rounded-lg border border-gray-200 p-3">
                  <p className="text-xs text-gray-500">Space complexity</p>
                  <p className="mt-1 font-mono text-sm">
                    {question.optimal_space_complexity || "Not specified"}
                  </p>
                </div>
              </div>
            </section>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3 border-t border-gray-200 p-4">
            <button
              type="button"
              onClick={() => goToQuestion(currentIndex - 1)}
              disabled={currentIndex === 0 || isFinished}
              className="inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </button>

            <button
              type="button"
              onClick={toggleReviewMark}
              disabled={isFinished}
              className="inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium transition hover:bg-gray-50 disabled:opacity-40"
            >
              <Flag className="h-4 w-4" />
              {isMarked ? "Remove review mark" : "Mark for review"}
            </button>

            <button
              type="button"
              onClick={() => goToQuestion(currentIndex + 1)}
              disabled={
                currentIndex === questions.length - 1 || isFinished
              }
              className="inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </section>

        <section className="min-w-0 overflow-hidden rounded-xl border border-gray-200 bg-white">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-gray-200 p-4">
            <div className="flex items-center gap-2">
              <Terminal className="h-5 w-5 text-gray-600" />
              <h2 className="font-semibold text-gray-900">Code editor</h2>
            </div>

            <label className="flex items-center gap-2 text-sm">
              <span className="text-gray-500">Language</span>
              <select
                value={language}
                disabled={isFinished}
                onChange={(event) =>
                  handleLanguageChange(
                    event.target.value as AssessmentLanguage,
                  )
                }
                className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:opacity-50"
              >
                <option value="python">Python</option>
                <option value="java">Java</option>
                <option value="cpp">C++</option>
              </select>
            </label>
          </div>

          <div className="overflow-hidden bg-[#1e1e1e]">
            <Editor
              height="420px"
              language={language === "cpp" ? "cpp" : language}
              theme="vs-dark"
              value={sourceCode}
              onChange={(value) => handleCodeChange(value ?? "")}
              options={{
                readOnly: isFinished,
                automaticLayout: true,
                autoIndent: "full",
                formatOnPaste: true,
                formatOnType: true,
                tabSize: 4,
                insertSpaces: true,
                detectIndentation: false,
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbers: "on",
                scrollBeyondLastLine: false,
                wordWrap: "on",
                bracketPairColorization: { enabled: true },
                autoClosingBrackets: "always",
                autoClosingQuotes: "always",
                suggestOnTriggerCharacters: true,
                padding: { top: 16, bottom: 16 },
              }}
            />
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3 border-t border-gray-200 p-4">
            <button
              type="button"
              onClick={handleReset}
              disabled={submitting || isFinished}
              className="inline-flex items-center gap-2 rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <RotateCcw className="h-4 w-4" />
              Reset code
            </button>

            <button
              type="button"
              onClick={() => void handleSubmit()}
              disabled={submitting || isFinished}
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {submitting ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Play className="h-4 w-4" />
              )}
              {submitting ? "Submitting..." : "Run & Submit"}
            </button>
          </div>

          {(runMessage || error) && (
            <div className="space-y-2 px-4 pb-4">
              {runMessage && (
                <p className="text-sm text-gray-500">{runMessage}</p>
              )}

              {error && (
                <div className="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                  <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                  <span>{error}</span>
                </div>
              )}
            </div>
          )}

          {currentResult && (
            <div className="border-t border-gray-200 p-4">
              <div className="mb-4 flex flex-wrap items-center gap-2">
                {isAccepted(currentResult) ? (
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                ) : (
                  <AlertCircle className="h-5 w-5 text-orange-500" />
                )}

                <h3 className="font-semibold text-gray-900">
                  Submission result
                </h3>

                <span
                  className={`ml-auto rounded-full px-3 py-1 text-xs font-semibold capitalize ${
                    isAccepted(currentResult)
                      ? "bg-green-100 text-green-700"
                      : "bg-orange-100 text-orange-700"
                  }`}
                >
                  {getVerdict(currentResult)}
                </span>
              </div>

              <p className="text-sm leading-6 text-gray-600">
                {currentResult.detail ?? "Submission completed."}
              </p>

              <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
                <div className="rounded-lg bg-gray-50 p-3">
                  <p className="text-xs text-gray-500">Tests passed</p>
                  <p className="mt-1 text-lg font-semibold text-gray-900">
                    {currentResult.tests_passed} / {currentResult.tests_total}
                  </p>
                </div>

                <div className="rounded-lg bg-gray-50 p-3">
                  <p className="text-xs text-gray-500">Verification</p>
                  <p
                    className={`mt-1 text-lg font-semibold ${
                      currentResult.verified
                        ? "text-green-700"
                        : "text-orange-700"
                    }`}
                  >
                    {currentResult.verified ? "Verified" : "Unverified"}
                  </p>
                </div>

                <div className="rounded-lg bg-gray-50 p-3">
                  <p className="text-xs text-gray-500">Metrics</p>
                  <p className="mt-1 text-lg font-semibold text-gray-900">
                    {currentResult.counts_toward_metrics
                      ? "Eligible"
                      : "Not counted"}
                  </p>
                </div>
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

export default AssessmentPage;
