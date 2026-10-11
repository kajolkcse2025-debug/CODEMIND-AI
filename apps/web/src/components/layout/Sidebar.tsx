import { NavLink } from "react-router-dom";

import { Wordmark } from "@/components/shared/Brand";
import { primaryNav, secondaryNav, type NavItem } from "@/components/layout/nav";
import { cn } from "@/lib/utils";

function NavRow({ item, onNavigate }: { item: NavItem; onNavigate?: (() => void) | undefined }) {
  return (
    <NavLink
      to={item.to}
      onClick={onNavigate}
      className={({ isActive }) =>
        cn(
          "relative flex items-center gap-3 rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground",
          isActive &&
            "bg-muted font-medium text-foreground before:absolute before:inset-y-1.5 before:left-0 before:w-0.5 before:rounded-full before:bg-primary",
        )
      }
    >
      <item.icon className="size-4 shrink-0" aria-hidden="true" />
      <span className="flex-1">{item.label}</span>
      {item.soon ? (
        <span className="rounded-sm border px-1.5 font-mono text-[10px] uppercase tracking-wide text-muted-foreground">
          Soon
        </span>
      ) : null}
    </NavLink>
  );
}

export function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <div className="flex h-full flex-col">
      <div className="px-5 py-5">
        <Wordmark />
      </div>
      <nav aria-label="Main" className="flex-1 space-y-0.5 px-3">
        {primaryNav.map((item) => (
          <NavRow key={item.to} item={item} onNavigate={onNavigate} />
        ))}
      </nav>
      <nav aria-label="Account" className="space-y-0.5 border-t px-3 py-3">
        {secondaryNav.map((item) => (
          <NavRow key={item.to} item={item} onNavigate={onNavigate} />
        ))}
      </nav>
    </div>
  );
}
