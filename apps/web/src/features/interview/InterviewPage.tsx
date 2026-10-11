import { ComingSoon } from "@/components/shared/ComingSoon";

export function InterviewPage() {
  return (
    <ComingSoon
      eyebrow="Practice"
      title="Interview"
      description="Mock interviews with follow-up questions and a rubric-based review."
      willInclude={[
        "Coding and technical interview practice",
        "Follow-up questions that adapt",
        "A written review of what went well and what to fix",
      ]}
    />
  );
}
