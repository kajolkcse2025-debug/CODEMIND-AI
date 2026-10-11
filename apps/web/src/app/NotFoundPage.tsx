import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";

export function NotFoundPage() {
  return (
    <div className="flex min-h-svh flex-col items-center justify-center px-6 text-center">
      <p className="font-mono text-sm text-muted-foreground">404</p>
      <h1 className="mt-2 text-3xl font-semibold">Page not found</h1>
      <p className="mt-3 max-w-sm text-sm text-muted-foreground">
        That page does not exist, or it has moved.
      </p>
      <Button className="mt-6" asChild>
        <Link to="/">Go home</Link>
      </Button>
    </div>
  );
}
