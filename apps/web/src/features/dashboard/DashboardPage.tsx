import { CircleCheck, Circle, Target } from "lucide-react";
import { Link } from "react-router-dom";

import { EmptyState } from "@/components/shared/EmptyState";
import { PageHeader } from "@/components/shared/PageHeader";
import { ProgressBar } from "@/components/shared/ProgressBar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useMe } from "@/features/me/hooks";
import { profileCompleteness } from "@/features/profile/completeness";

export function DashboardPage() {
  const me = useMe();
  const profile = me.data?.profile ?? null;
  const completeness = profile ? profileCompleteness(profile) : null;
  const firstName = profile?.name.trim().split(/\s+/)[0];

  const steps = [
    { label: "Create your account", done: true, note: null },
    { label: "Set up your profile", done: profile !== null, note: null },
    { label: "Take the diagnostic assessment", done: false, note: "Not available yet" },
    { label: "Get your first daily mission", done: false, note: "Needs the diagnostic" },
  ];

  return (
    <>
      <PageHeader
        eyebrow="Today"
        title={firstName ? `Welcome, ${firstName}` : "Welcome"}
        description="Your daily mission will live here once CodeMind has something real to base it on."
      />

      <div className="grid gap-6 lg:grid-cols-3">
        <section aria-labelledby="mission-heading" className="lg:col-span-2">
          <Card className="h-full">
            <CardHeader>
              <CardTitle id="mission-heading">Today&apos;s mission</CardTitle>
              <CardDescription>What to practise today, and why.</CardDescription>
            </CardHeader>
            <CardContent>
              <EmptyState
                icon={Target}
                title="No mission yet"
                description="Missions are built from your diagnostic results, weaknesses and roadmap. None of those exist yet, so there is nothing honest to show. This arrives in a later release."
              />
            </CardContent>
          </Card>
        </section>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Setup</CardTitle>
              <CardDescription>Where you are in getting started.</CardDescription>
            </CardHeader>
            <CardContent>
              <ol className="space-y-3 text-sm">
                {steps.map((step) => (
                  <li key={step.label} className="flex items-start gap-3">
                    {step.done ? (
                      <CircleCheck
                        className="mt-0.5 size-4 shrink-0 text-success"
                        aria-label="Done"
                      />
                    ) : (
                      <Circle
                        className="mt-0.5 size-4 shrink-0 text-muted-foreground"
                        aria-label="Not done"
                      />
                    )}
                    <span className={step.done ? "" : "text-muted-foreground"}>
                      {step.label}
                      {step.note ? <span className="block text-xs">{step.note}</span> : null}
                    </span>
                  </li>
                ))}
              </ol>
            </CardContent>
          </Card>

          {completeness ? (
            <Card>
              <CardHeader>
                <CardTitle>Profile</CardTitle>
                <CardDescription>
                  {completeness.filled} of {completeness.total} optional details filled in.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <ProgressBar value={completeness.percent} label="Profile completeness" />
                {completeness.missing.length > 0 ? (
                  <p className="text-xs text-muted-foreground">
                    Missing: {completeness.missing.join(", ")}.
                  </p>
                ) : null}
                <Button variant="outline" size="sm" asChild>
                  <Link to="/profile">Edit profile</Link>
                </Button>
              </CardContent>
            </Card>
          ) : null}
        </div>
      </div>
    </>
  );
}
