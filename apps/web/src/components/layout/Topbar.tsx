import { LogOut, Menu, Settings, User } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { Sidebar } from "@/components/layout/Sidebar";
import { ThemeToggle } from "@/components/shared/ThemeToggle";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { useAuth } from "@/features/auth/auth-context";
import { useMe } from "@/features/me/hooks";
import { useState } from "react";

export function Topbar() {
  const { user, signOut } = useAuth();
  const me = useMe();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const name = me.data?.profile?.name ?? user?.displayName ?? user?.email ?? "Account";
  const initial = name.trim().charAt(0).toUpperCase() || "?";

  return (
    <div className="sticky top-0 z-30 flex h-14 items-center gap-2 border-b bg-background/90 px-4 backdrop-blur lg:px-8">
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetTrigger asChild>
          <Button variant="ghost" size="icon" className="lg:hidden" aria-label="Open menu">
            <Menu />
          </Button>
        </SheetTrigger>
        <SheetContent>
          <SheetTitle className="sr-only">Navigation</SheetTitle>
          <SheetDescription className="sr-only">Main navigation menu</SheetDescription>
          <Sidebar onNavigate={() => setOpen(false)} />
        </SheetContent>
      </Sheet>
      <div className="flex-1" />
      <ThemeToggle />
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" className="gap-2 px-2" aria-label="Account menu">
            <span className="flex size-7 items-center justify-center rounded-full bg-accent font-mono text-xs text-accent-foreground">
              {initial}
            </span>
            <span className="hidden max-w-40 truncate text-sm sm:inline">{name}</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          {user?.email ? <DropdownMenuLabel>{user.email}</DropdownMenuLabel> : null}
          <DropdownMenuItem onSelect={() => navigate("/profile")}>
            <User className="size-4" /> Profile
          </DropdownMenuItem>
          <DropdownMenuItem onSelect={() => navigate("/settings")}>
            <Settings className="size-4" /> Settings
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem onSelect={() => void signOut()}>
            <LogOut className="size-4" /> Sign out
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
