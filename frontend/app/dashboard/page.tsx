// app/dashboard/page.tsx
"use client";

import { useUser } from "@clerk/nextjs";
import { DashboardSidebar } from "@/components/dashboard/DashboardSidebar";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { Greeting } from "@/components/dashboard/Greeting";
import { MetricsGrid } from "@/components/dashboard/MetricsGrid";
import { WorkflowStatus } from "@/components/dashboard/WorkflowStatus";
import { RecentTickets } from "@/components/dashboard/RecentTickets";
import { CreateWorkspaceCard } from "@/components/dashboard/CreateWorkspaceCard";
import { YourWorkspaces } from "@/components/dashboard/YourWorkspaces";
import { RecentExports } from "@/components/dashboard/RecentExports";
import { SupportAutomationCard } from "@/components/dashboard/SupportAutomationCard";
import { mockDashboardData } from "@/lib/mock/dashboard";

export default function DashboardPage() {
  const { isLoaded, user } = useUser();

  // Show loading spinner while Clerk initializes
  if (!isLoaded) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#0B0F19]">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
      </div>
    );
  }

  const userName = user?.fullName || user?.username || "User";

  return (
    <div className="min-h-screen bg-[#0B0F19] text-slate-200">
      <DashboardSidebar />

      <div className="lg:pl-64">
        {/* ✅ No props needed - Header gets user data internally via useUser() */}
        <DashboardHeader />

        <main className="mx-auto max-w-7xl p-6">
          <Greeting userName={userName} />

          <MetricsGrid metrics={mockDashboardData.metrics} />

          <div className="mt-6 grid grid-cols-1 gap-6 xl:grid-cols-3">
            <div className="xl:col-span-2 space-y-6">
              <WorkflowStatus steps={mockDashboardData.workflowSteps} />
              <RecentTickets workspaces={mockDashboardData.recentTickets} />
            </div>

            <div className="space-y-6">
              <CreateWorkspaceCard />
              <YourWorkspaces workspaces={mockDashboardData.workspaces} viewAllHref="/workspaces" />
              <RecentExports exports={mockDashboardData.exports} />
              <SupportAutomationCard />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}