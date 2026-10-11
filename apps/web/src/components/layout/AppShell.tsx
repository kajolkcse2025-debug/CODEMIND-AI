import { Outlet } from "react-router-dom";

import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";
import { VerifyEmailBanner } from "@/components/layout/VerifyEmailBanner";

export function AppShell() {
  return (
    <div className="min-h-svh">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:fixed focus:left-3 focus:top-3 focus:z-50 focus:rounded-md focus:bg-primary focus:px-3 focus:py-2 focus:text-primary-foreground"
      >
        Skip to content
      </a>
      <aside className="fixed inset-y-0 left-0 hidden w-60 border-r bg-card lg:block">
        <Sidebar />
      </aside>
      <div className="lg:pl-60">
        <Topbar />
        <VerifyEmailBanner />
        <main id="main" className="mx-auto w-full max-w-5xl px-4 py-8 lg:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
