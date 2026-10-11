import { ComingSoon } from "@/components/shared/ComingSoon";

export function RoadmapPage() {
  return (
    <ComingSoon
      eyebrow="Plan"
      title="Roadmap"
      description="A study plan that adapts to your results, goals and available time."
      willInclude={[
        "Topics ordered by prerequisites and your weaknesses",
        "An honest view of what fits before your deadline",
        "A clear explanation whenever the plan changes",
      ]}
    />
  );
}
