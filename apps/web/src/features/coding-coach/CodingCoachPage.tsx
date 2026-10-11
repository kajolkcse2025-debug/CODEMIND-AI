import { ComingSoon } from "@/components/shared/ComingSoon";

export function CodingCoachPage() {
  return (
    <ComingSoon
      eyebrow="Mentor"
      title="Coding coach"
      description="Submit code and get explanations, complexity analysis and progressive hints."
      willInclude={[
        "Bug explanations and edge cases",
        "Complexity analysis and optimisation ideas",
        "Hints first, full solutions last",
      ]}
    />
  );
}
