import { createBrowserRouter, createMemoryRouter, type RouteObject } from "react-router-dom";

import { AppShell } from "@/components/layout/AppShell";
import { NotFoundPage } from "@/app/NotFoundPage";
import { OnboardingOnly, PublicOnly, RequireAuth, RequireProfile } from "@/app/guards";
import { RouteError } from "@/app/RouteError";
import { AnalyticsPage } from "@/features/analytics/AnalyticsPage";
import { AssessmentPage } from "@/features/assessment/AssessmentPage";
import { ForgotPasswordPage } from "@/features/auth/ForgotPasswordPage";
import { LoginPage } from "@/features/auth/LoginPage";
import { RegisterPage } from "@/features/auth/RegisterPage";
import { CodingCoachPage } from "@/features/coding-coach/CodingCoachPage";
import { CodingDnaPage } from "@/features/coding-dna/CodingDnaPage";
import { DashboardPage } from "@/features/dashboard/DashboardPage";
import { InterviewPage } from "@/features/interview/InterviewPage";
import { LandingPage } from "@/features/landing/LandingPage";
import { MissionsPage } from "@/features/missions/MissionsPage";
import { OnboardingPage } from "@/features/profile/OnboardingPage";
import { ProfilePage } from "@/features/profile/ProfilePage";
import { RoadmapPage } from "@/features/roadmap/RoadmapPage";
import { SettingsPage } from "@/features/settings/SettingsPage";

export const routes: RouteObject[] = [
  {
    errorElement: <RouteError />,
    children: [
      { path: "/", element: <LandingPage /> },
      {
        element: <PublicOnly />,
        children: [
          { path: "/login", element: <LoginPage /> },
          { path: "/register", element: <RegisterPage /> },
          { path: "/forgot-password", element: <ForgotPasswordPage /> },
        ],
      },
      {
        element: <RequireAuth />,
        children: [
          {
            element: <OnboardingOnly />,
            children: [{ path: "/onboarding", element: <OnboardingPage /> }],
          },
          {
            element: <RequireProfile />,
            children: [
              {
                element: <AppShell />,
                children: [
                  { path: "/dashboard", element: <DashboardPage /> },
                  { path: "/assessment", element: <AssessmentPage /> },
                  { path: "/coding-coach", element: <CodingCoachPage /> },
                  { path: "/roadmap", element: <RoadmapPage /> },
                  { path: "/missions", element: <MissionsPage /> },
                  { path: "/analytics", element: <AnalyticsPage /> },
                  { path: "/coding-dna", element: <CodingDnaPage /> },
                  { path: "/interview", element: <InterviewPage /> },
                  { path: "/profile", element: <ProfilePage /> },
                  { path: "/settings", element: <SettingsPage /> },
                ],
              },
            ],
          },
        ],
      },
      { path: "*", element: <NotFoundPage /> },
    ],
  },
];

export const createAppRouter = () => createBrowserRouter(routes);
export const createTestRouter = (initialEntries: string[]) =>
  createMemoryRouter(routes, { initialEntries });
