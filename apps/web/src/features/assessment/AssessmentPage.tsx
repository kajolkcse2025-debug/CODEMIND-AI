import { ComingSoon } from "@/components/shared/ComingSoon";

export function AssessmentPage() {
  return (
    <ComingSoon
      eyebrow="Diagnostic"
      title="Assessment"
      description="A short timed diagnostic that finds your real starting level."
      willInclude={[
        "Three rounds, from easy to advanced, across the core topics",
        "Your level, strengths and weaknesses with honest confidence",
        "A starting point for your Coding DNA and roadmap",
      ]}
    />
  );
}
