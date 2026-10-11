import { ComingSoon } from "@/components/shared/ComingSoon";

export function MissionsPage() {
  return (
    <ComingSoon
      eyebrow="Daily"
      title="Missions"
      description="Your daily practice set, sized to the time you actually have."
      willInclude={[
        "Problems matched to your weaknesses and roadmap",
        "Revision of things you are about to forget",
        "A reason shown for every item",
      ]}
    />
  );
}
