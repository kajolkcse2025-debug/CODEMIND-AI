
import { useState } from "react";
import { Link, useParams } from "react-router-dom";

type Language = "Python" | "Java" | "C++";

const examples: Record<Language, string> = {
  Python: `# Create an array (list)
numbers = [10, 20, 30, 40]

# Access an element
print(numbers[0])  # 10

# Update an element
numbers[1] = 25

# Add an element
numbers.append(50)

# Traverse the array
for number in numbers:
    print(number)`,
  Java: `// Create an array
int[] numbers = {10, 20, 30, 40};

// Access an element
System.out.println(numbers[0]); // 10

// Update an element
numbers[1] = 25;

// Traverse the array
for (int i = 0; i < numbers.length; i++) {
    System.out.println(numbers[i]);
}`,
  "C++": `#include <iostream>
using namespace std;

int main() {
    // Create an array
    int numbers[] = {10, 20, 30, 40};

    // Access an element
    cout << numbers[0] << endl; // 10

    // Update an element
    numbers[1] = 25;

    // Traverse the array
    for (int i = 0; i < 4; i++) {
        cout << numbers[i] << endl;
    }

    return 0;
}`,
};

const quizQuestions = [
  {
    question: "What is the index of the first element in a typical array?",
    options: ["1", "0", "-1", "It depends on the array size"],
    answer: 1,
    explanation:
      "Most commonly used languages such as Python, Java and C++ use zero-based indexing. The first element is at index 0.",
  },
  {
    question: "What is the time complexity of accessing an array element by index?",
    options: ["O(n)", "O(log n)", "O(1)", "O(n²)"],
    answer: 2,
    explanation:
      "Arrays support direct access by index, so accessing an element takes constant time: O(1).",
  },
  {
    question: "What is the time complexity of searching an unsorted array for a value?",
    options: ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
    answer: 2,
    explanation:
      "In the worst case, you may need to inspect every element. That is linear time, O(n).",
  },
];

export function TopicLearningPage() {
  const { topicSlug } = useParams();
  const [language, setLanguage] = useState<Language>("Python");
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [submitted, setSubmitted] = useState(false);

  const isArrays = topicSlug === "arrays";

  if (!isArrays) {
    return (
      <div className="mx-auto max-w-4xl space-y-5">
        <Link
          to="/roadmap"
          className="text-sm font-medium text-primary hover:underline"
        >
          ← Back to roadmap
        </Link>
        <section className="rounded-2xl border border-border bg-card p-6">
          <p className="text-xs font-semibold uppercase tracking-wider text-primary">
            CodeMind learning space
          </p>
          <h1 className="mt-2 text-2xl font-bold capitalize">
            {topicSlug?.replaceAll("-", " ") ?? "Topic"}
          </h1>
          <p className="mt-3 text-sm leading-6 text-muted-foreground">
            This lesson is being prepared. The Arrays lesson is available now.
            We'll add the remaining topic lessons to this learning space next.
          </p>
          <Link
            to="/learn/arrays"
            className="mt-5 inline-flex rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground"
          >
            Open Arrays lesson
          </Link>
        </section>
      </div>
    );
  }

  const score = quizQuestions.reduce(
    (total, question, index) =>
      total + (answers[index] === question.answer ? 1 : 0),
    0,
  );

  return (
    <div className="mx-auto max-w-5xl space-y-8">
      <div className="space-y-3">
        <Link
          to="/roadmap"
          className="text-sm font-medium text-primary hover:underline"
        >
          ← Back to roadmap
        </Link>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-primary">
            CodeMind learning space · DSA foundations
          </p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight">Arrays</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
            Learn how arrays store data, access elements, and form the
            foundation of many important coding interview patterns.
          </p>
        </div>
        <div className="flex flex-wrap gap-2 text-xs">
          <span className="rounded-full bg-primary/10 px-3 py-1 font-medium text-primary">
            Beginner
          </span>
          <span className="rounded-full bg-muted px-3 py-1 text-muted-foreground">
            20–30 minutes
          </span>
          <span className="rounded-full bg-muted px-3 py-1 text-muted-foreground">
            Lesson 1
          </span>
        </div>
      </div>

      <section className="space-y-3">
        <h2 className="text-xl font-bold">1. What is an array?</h2>
        <p className="text-sm leading-7 text-muted-foreground">
          An array is a data structure that stores multiple values in an
          ordered sequence. Each value has a position called an index. You can
          use that index to access or update an element.
        </p>
        <div className="rounded-2xl border border-border bg-card p-5">
          <p className="mb-4 text-sm font-semibold">Example: an array of marks</p>
          <div className="grid grid-cols-5 gap-2">
            {[72, 85, 90, 68, 95].map((value, index) => (
              <div key={index} className="text-center">
                <div className="rounded-lg border border-primary/30 bg-primary/5 py-4 text-lg font-bold">
                  {value}
                </div>
                <p className="mt-2 text-xs text-muted-foreground">
                  Index {index}
                </p>
              </div>
            ))}
          </div>
          <p className="mt-4 text-xs leading-5 text-muted-foreground">
            The first value, 72, is at index 0. The last value, 95, is at
            index 4.
          </p>
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-bold">2. Important operations</h2>
        <div className="grid gap-3 sm:grid-cols-2">
          {[
            {
              name: "Access",
              complexity: "O(1)",
              detail: "Read a value using its index.",
            },
            {
              name: "Update",
              complexity: "O(1)",
              detail: "Replace a value at a known index.",
            },
            {
              name: "Search",
              complexity: "O(n)",
              detail: "Find a value in an unsorted array.",
            },
            {
              name: "Insert / Delete",
              complexity: "O(n)",
              detail: "May require shifting other elements.",
            },
          ].map((operation) => (
            <div
              key={operation.name}
              className="rounded-xl border border-border bg-card p-4"
            >
              <div className="flex items-center justify-between gap-2">
                <h3 className="font-semibold">{operation.name}</h3>
                <code className="rounded bg-muted px-2 py-1 text-xs">
                  {operation.complexity}
                </code>
              </div>
              <p className="mt-2 text-sm text-muted-foreground">
                {operation.detail}
              </p>
            </div>
          ))}
        </div>
        <p className="text-xs leading-5 text-muted-foreground">
          Note: inserting or deleting at the end of a dynamic array can be
          faster on average. The O(n) cost applies when elements need to shift.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-bold">3. Code it yourself</h2>
        <p className="text-sm text-muted-foreground">
          Select your preferred language and study how an array is created,
          accessed, updated and traversed.
        </p>
        <div className="overflow-hidden rounded-2xl border border-border bg-card">
          <div className="flex flex-wrap gap-2 border-b border-border p-3">
            {(["Python", "Java", "C++"] as Language[]).map((item) => (
              <button
                key={item}
                type="button"
                onClick={() => setLanguage(item)}
                className={`rounded-lg px-3 py-2 text-sm font-medium ${
                  language === item
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground hover:text-foreground"
                }`}
              >
                {item}
              </button>
            ))}
          </div>
          <pre className="overflow-x-auto p-4 text-sm leading-6">
            <code>{examples[language]}</code>
          </pre>
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-bold">4. Patterns to learn next</h2>
        <div className="space-y-3">
          {[
            ["Array traversal", "Visit every element using a loop."],
            ["Two pointers", "Use two indices to solve problems efficiently."],
            ["Sliding window", "Process a continuous section of an array."],
            ["Prefix sums", "Precompute running totals for range queries."],
            ["Hashing with arrays", "Use maps or frequency arrays to count values."],
          ].map(([name, description], index) => (
            <div
              key={name}
              className="flex gap-3 rounded-xl border border-border bg-card p-4"
            >
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted text-sm font-semibold">
                {index + 1}
              </span>
              <div>
                <h3 className="text-sm font-semibold">{name}</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  {description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="space-y-4 rounded-2xl border border-border bg-card p-5">
        <div>
          <h2 className="text-xl font-bold">5. Check your understanding</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Answer all three questions. You can review your answers before
            submitting.
          </p>
        </div>

        {quizQuestions.map((question, questionIndex) => (
          <div key={question.question} className="space-y-3">
            <p className="text-sm font-semibold">
              {questionIndex + 1}. {question.question}
            </p>
            <div className="grid gap-2 sm:grid-cols-2">
              {question.options.map((option, optionIndex) => {
                const selected = answers[questionIndex] === optionIndex;
                const correct = question.answer === optionIndex;
                const showResult = submitted;

                return (
                  <button
                    key={option}
                    type="button"
                    disabled={submitted}
                    onClick={() =>
                      setAnswers((previous) => ({
                        ...previous,
                        [questionIndex]: optionIndex,
                      }))
                    }
                    className={`rounded-lg border p-3 text-left text-sm transition ${
                      showResult && correct
                        ? "border-success bg-success/10"
                        : showResult && selected
                          ? "border-destructive bg-destructive/10"
                          : selected
                            ? "border-primary bg-primary/10"
                            : "border-border hover:border-primary/50"
                    }`}
                  >
                    {option}
                  </button>
                );
              })}
            </div>
            {submitted && (
              <p className="rounded-lg bg-muted p-3 text-xs leading-5 text-muted-foreground">
                {question.explanation}
              </p>
            )}
          </div>
        ))}

        {!submitted ? (
          <button
            type="button"
            disabled={Object.keys(answers).length !== quizQuestions.length}
            onClick={() => setSubmitted(true)}
            className="rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground disabled:cursor-not-allowed disabled:opacity-50"
          >
            Submit answers
          </button>
        ) : (
          <div className="rounded-xl bg-muted p-4">
            <p className="font-semibold">
              Your score: {score}/{quizQuestions.length}
            </p>
            <p className="mt-1 text-sm text-muted-foreground">
              {score === quizQuestions.length
                ? "Excellent! You understand the fundamentals of arrays."
                : "Review the explanations above, then try these concepts again."}
            </p>
            <button
              type="button"
              onClick={() => {
                setAnswers({});
                setSubmitted(false);
              }}
              className="mt-3 text-sm font-semibold text-primary hover:underline"
            >
              Try quiz again
            </button>
          </div>
        )}
      </section>

      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-border pt-5">
        <Link
          to="/roadmap"
          className="rounded-lg border border-border px-4 py-2.5 text-sm font-semibold hover:bg-muted"
        >
          Back to roadmap
        </Link>
        <p className="text-xs text-muted-foreground">
          Finish the lesson and practice problems before completing this topic.
        </p>
      </div>
    </div>
  );
}
