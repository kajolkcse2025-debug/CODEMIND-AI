
export interface AssessmentTopicScore {
  topic: string;
  correct: number;
  total: number;
}

export interface AssessmentHistoryEntry {
  id: string;
  completedAt: string;
  score: number;
  totalQuestions: number;
  correctAnswers: number;
  durationSeconds: number;
  topicScores: AssessmentTopicScore[];
}

const STORAGE_KEY = "codemind_assessment_history_v1";
const MAX_ENTRIES = 100;

function isValidEntry(value: unknown): value is AssessmentHistoryEntry {
  if (!value || typeof value !== "object") return false;

  const entry = value as AssessmentHistoryEntry;

  return (
    typeof entry.id === "string" &&
    typeof entry.completedAt === "string" &&
    typeof entry.score === "number" &&
    typeof entry.totalQuestions === "number" &&
    typeof entry.correctAnswers === "number" &&
    typeof entry.durationSeconds === "number" &&
    Array.isArray(entry.topicScores)
  );
}

export function getAssessmentHistory(): AssessmentHistoryEntry[] {
  if (typeof window === "undefined") return [];

  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (!stored) return [];

    const parsed: unknown = JSON.parse(stored);
    if (!Array.isArray(parsed)) return [];

    return parsed.filter(isValidEntry);
  } catch {
    return [];
  }
}

export function saveAssessmentResult(
  result: Omit<AssessmentHistoryEntry, "id" | "completedAt">,
): AssessmentHistoryEntry {
  const entry: AssessmentHistoryEntry = {
    ...result,
    id: crypto.randomUUID(),
    completedAt: new Date().toISOString(),
  };

  const history = getAssessmentHistory();
  const updated = [entry, ...history].slice(0, MAX_ENTRIES);

  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));

  return entry;
}

export function clearAssessmentHistory(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(STORAGE_KEY);
}

export function getAssessmentAnalytics() {
  const history = getAssessmentHistory();

  const completed = history.length;
  const totalQuestions = history.reduce(
    (sum, item) => sum + item.totalQuestions,
    0,
  );
  const totalCorrect = history.reduce(
    (sum, item) => sum + item.correctAnswers,
    0,
  );

  const averageScore =
    completed === 0
      ? 0
      : Math.round(
          history.reduce((sum, item) => sum + item.score, 0) / completed,
        );

  const overallAccuracy =
    totalQuestions === 0
      ? 0
      : Math.round((totalCorrect / totalQuestions) * 100);

  const topicMap = new Map<
    string,
    { correct: number; total: number }
  >();

  for (const attempt of history) {
    for (const topic of attempt.topicScores) {
      const current = topicMap.get(topic.topic) ?? {
        correct: 0,
        total: 0,
      };

      current.correct += topic.correct;
      current.total += topic.total;
      topicMap.set(topic.topic, current);
    }
  }

  const topics = Array.from(topicMap.entries())
    .map(([topic, values]) => ({
      topic,
      correct: values.correct,
      total: values.total,
      accuracy:
        values.total === 0
          ? 0
          : Math.round((values.correct / values.total) * 100),
    }))
    .sort((a, b) => a.accuracy - b.accuracy);

  return {
    completed,
    averageScore,
    overallAccuracy,
    totalQuestions,
    totalCorrect,
    strongestTopic: [...topics].sort(
      (a, b) => b.accuracy - a.accuracy,
    )[0] ?? null,
    weakestTopic: topics[0] ?? null,
    topics,
    recentAttempts: history.slice(0, 10),
  };
}
