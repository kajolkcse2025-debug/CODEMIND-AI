import { ComingSoon } from "@/components/shared/ComingSoon";

export function CodingDnaPage() {
  return (
    <ComingSoon
      eyebrow="Profile"
      title="Coding DNA"
      description="A behavioural profile of how you solve problems, evolving as you practise."
      willInclude={[
        "Traits such as debugging, optimisation and time management",
        "Clear calibrating states until there is enough evidence",
        "How your habits change over time",
      ]}
    />
  );
}
