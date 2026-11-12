import {
  BarChart3,
  Brain,
  Dna,
  LayoutDashboard,
  ListChecks,
  MessagesSquare,
  Route,
  Settings,
  Target,
  User,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
  /** True for modules that are not built yet (shown with a "Soon" tag). */
  soon?: boolean;
}

export const primaryNav: NavItem[] = [
  { to: "/dashboard", label: "Today", icon: LayoutDashboard },
  { to: "/assessment", label: "Assessment", icon: Target },
  { to: "/coding-coach", label: "Coding coach", icon: Brain, soon: true },
  { to: "/roadmap", label: "Roadmap", icon: Route, soon: true },
  { to: "/missions", label: "Missions", icon: ListChecks, soon: true },
  { to: "/analytics", label: "Analytics", icon: BarChart3, soon: true },
  { to: "/coding-dna", label: "Coding DNA", icon: Dna, soon: true },
  { to: "/interview", label: "Interview", icon: MessagesSquare, soon: true },
];

export const secondaryNav: NavItem[] = [
  { to: "/profile", label: "Profile", icon: User },
  { to: "/settings", label: "Settings", icon: Settings },
];
