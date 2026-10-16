import { Link, Navigate } from "react-router-dom";

import { Wordmark } from "@/components/shared/Brand";
import { ThemeToggle } from "@/components/shared/ThemeToggle";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/features/auth/auth-context";

const principles = [
  {
    title: "Numbers will come from code",
    body: "Scores are being built as deterministic logic you can audit. AI will explain and coach. It will never grade you.",
  },
  {
    title: "Honest about uncertainty",
    body: "When there is not enough evidence, CodeMind will say so instead of inventing a number.",
  },
  {
    title: "Only verified work will count",
    body: "Results that a real code runner did not check will never affect your progress.",
  },
];

export function LandingPage() {
  const { status } = useAuth();
  if (status === "authenticated") return <Navigate to="/dashboard" replace />;

  return (
    <div className="flex min-h-svh flex-col">
      <header className="mx-auto flex w-full max-w-5xl items-center justify-between px-6 py-5">
        <Wordmark />
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <Button variant="ghost" asChild>
            <Link to="/login">Sign in</Link>
          </Button>
          <Button asChild>
            <Link to="/register">Create account</Link>
          </Button>
        </div>
      </header>
      <main className="mx-auto w-full max-w-5xl flex-1 px-6">
        <section className="py-16 sm:py-24">
          <Badge variant="outline" className="mb-6 font-mono">
            Early development
          </Badge>
          <h1 className="max-w-3xl text-4xl font-semibold leading-[1.1] sm:text-6xl">
            A coding mentor that adapts to how you actually practice.
          </h1>
          <p className="mt-6 max-w-xl text-lg text-muted-foreground">
            CodeMind is being built to learn from your attempts, mistakes and pace, then tell you
            what to do today. Right now you can create an account and set up your profile. The
            diagnostic, daily missions and coach arrive in later releases.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Button size="lg" asChild>
              <Link to="/register">Get started</Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link to="/login">I already have an account</Link>
            </Button>
          </div>
        </section>
        <section
          aria-label="Design principles"
          className="grid gap-px overflow-hidden rounded-lg border bg-border sm:grid-cols-3"
        >
          {principles.map((item, index) => (
            <div key={item.title} className="bg-card p-6">
              <p className="font-mono text-xs text-muted-foreground">0{index + 1}</p>
              <h2 className="mt-3 text-base font-semibold">{item.title}</h2>
              <p className="mt-2 text-sm text-muted-foreground">{item.body}</p>
            </div>
          ))}
        </section>
      </main>
      <footer className="mx-auto w-full max-w-5xl px-6 py-10 text-xs text-muted-foreground">
        CodeMind AI. Readiness and progress figures, when they arrive, are estimates of preparation,
        not predictions of hiring outcomes.
      </footer>
    </div>
  );
}
