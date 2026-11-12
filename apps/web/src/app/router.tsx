
import {
  createBrowserRouter,
  createMemoryRouter,
  type InitialEntry,
  type RouteObject,
} from "react-router-dom";

import { AppShell } from "@/components/layout/AppShell";
import { NotFoundPage } from "@/app/NotFoundPage";
import {
  OnboardingOnly,
  PublicOnly,
  RequireAuth,
  RequireProfile,
} from "@/app/guards";
import { RouteError } from "@/app/RouteError";

import { AnalyticsPage } from "@/features/analytics/AnalyticsPage";
import { AssessmentPage } from "@/features/assessment/AssessmentPage";
import AssessmentHistoryPage from "@/features/assessment/AssessmentHistoryPage";
import { TopicLearningPage } from "@/features/roadmap/TopicLearningPage";

import { ForgotPasswordPage } from "@/features/auth/ForgotPasswordPage";
import { LoginPage } from "@/features/auth/LoginPage";
import { RegisterPage } from "@/features/auth/RegisterPage";

import { OnboardingPage } from "@/features/profile/OnboardingPage";
import { DashboardPage } from "@/features/dashboard/DashboardPage";
import { CodingCoachPage } from "@/features/coding-coach/CodingCoachPage";
import { CodingProblemPage } from "@/features/coding-coach/CodingProblemPage";
import { RoadmapPage } from "@/features/roadmap/RoadmapPage";
import { MissionsPage } from "@/features/missions/MissionsPage";
import { CodingDnaPage } from "@/features/coding-dna/CodingDnaPage";
import { InterviewPage } from "@/features/interview/InterviewPage";
import { ProfilePage } from "@/features/profile/ProfilePage";
import { SettingsPage } from "@/features/settings/SettingsPage";

const routes: RouteObject[] = [
  {
    errorElement: <RouteError />,
    children: [
      {
        element: <PublicOnly />,
        children: [
          { path: "/", element: <LoginPage /> },
          { path: "/login", element: <LoginPage /> },
          { path: "/register", element: <RegisterPage /> },
          {
            path: "/forgot-password",
            element: <ForgotPasswordPage />,
          },
        ],
      },
      {
        element: <RequireAuth />,
        children: [
          {
            element: <OnboardingOnly />,
            children: [
              {
                path: "/onboarding",
                element: <OnboardingPage />,
              },
            ],
          },
          {
            element: <RequireProfile />,
            children: [
              {
                element: <AppShell />,
                children: [
                  { path: "/dashboard", element: <DashboardPage /> },
                  { path: "/assessment", element: <AssessmentPage /> },
                  {
                    path: "/assessment/history",
                    element: <AssessmentHistoryPage />,
                  },
                  {
                    path: "/coding-coach",
                    element: <CodingCoachPage />,
                  },
                  {
                    path: "/coding-coach/:slug",
                    element: <CodingProblemPage />,
                  },
                  { path: "/roadmap", element: <RoadmapPage /> },
                  { path: "/learn/:topicSlug", element: <TopicLearningPage /> },
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

export const createTestRouter = (initialEntries: InitialEntry[]) =>
  createMemoryRouter(routes, { initialEntries });
