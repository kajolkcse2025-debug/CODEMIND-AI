import { ComingSoon } from "@/components/shared/ComingSoon";

export function AnalyticsPage() {
  return (
    <ComingSoon
      eyebrow="Progress"
      title="Analytics"
      description="Topic-by-topic performance, with confidence shown alongside every number."
      willInclude={[
        "Solved counts, accuracy and solving time per topic",
        "Mastery that says how sure it is",
        "Trends over time",
      ]}
    />
  );
}
