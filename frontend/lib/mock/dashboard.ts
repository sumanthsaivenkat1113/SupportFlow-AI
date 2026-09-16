// lib/mock/dashboard.ts
import { DashboardData } from "@/types/dashboard";

export const mockDashboardData: DashboardData = {
  user: {
    name: "Sumanth",
    organization: "Acme Corp",
    avatarUrl: "/avatars/sumanth.jpg",
  },
  metrics: [
    {
      title: "Total Tickets",
      value: 248,
      change: { value: "+12%", direction: "up" },
      description: "vs. last 7 days",
      variant: "blue",
    },
    {
      title: "Auto Resolved",
      value: 182,
      change: { value: "+18%", direction: "up" },
      description: "73.4% of total",
      variant: "purple",
    },
    {
      title: "Needs Human Review",
      value: 58,
      change: { value: "-8%", direction: "down" },
      description: "23.4% of total",
      variant: "green",
    },
    {
      title: "Avg. Resolution Time",
      value: "2.6 min",
      change: { value: "-32%", direction: "down" },
      description: "vs. last 7 days",
      variant: "orange",
    },
  ],
  workflowSteps: [
    { id: 1, title: "Upload & Parse", subtitle: "PDFs → Text (chunks)", icon: "upload" },
    { id: 2, title: "Create Embeddings", subtitle: "Store in Vector DB", icon: "database" },
    { id: 3, title: "Classify Tickets", subtitle: "Auto or Human", icon: "tag" },
    { id: 4, title: "RAG Search", subtitle: "Top 3–5 relevant chunks", icon: "search" },
    { id: 5, title: "Generate Response", subtitle: "Grounded with context", icon: "sparkles" },
    { id: 6, title: "Export Results", subtitle: "JSON / Excel / CSV", icon: "download" },
  ],
  recentTickets: [
    {
      workspaceId: "ws-1",
      workspaceName: "Acme Corp",
      tickets: [
        { id: "#TKT-001", customer: "Acme Corp", subject: "Unable to access account", category: "Account", status: "automated", resolution: "Provided account reset...", createdAt: "2025-09-15" },
        { id: "#TKT-002", customer: "Globex", subject: "Refund not received", category: "Billing", status: "human-review", createdAt: "2025-09-14" },
        { id: "#TKT-003", customer: "Initech", subject: "Feature not working", category: "Technical", status: "automated", resolution: "Shared step-by-step guide", createdAt: "2025-09-14" },
      ],
    },
    {
      workspaceId: "ws-2",
      workspaceName: "Umbrella Co.",
      tickets: [
        { id: "#TKT-004", customer: "Umbrella Co.", subject: "Request for invoice", category: "Billing", status: "automated", resolution: "Sent invoice via email", createdAt: "2025-09-13" },
        { id: "#TKT-005", customer: "Wayne Enterprises", subject: "Login issue", category: "Account", status: "human-review", createdAt: "2025-09-13" },
        { id: "#TKT-006", customer: "Stark Industries", subject: "Product not working", category: "Technical", status: "automated", resolution: "Provided troubleshooting...", createdAt: "2025-09-12" },
      ],
    },
  ],
  workspaces: [
    { id: "w-1", name: "Acme Corp", documentCount: 12, ticketCount: 248, status: "active" },
    { id: "w-2", name: "Globex", documentCount: 5, ticketCount: 134, status: "active" },
    { id: "w-3", name: "Initech", documentCount: 3, ticketCount: 87, status: "active" },
  ],
  exports: [
    { id: "e-1", fileName: "supportflow_results_2025-08-30.json", format: "json", createdAt: "Aug 30, 2025", ticketCount: 248 },
    { id: "e-2", fileName: "acme_tickets_aug.csv", format: "csv", createdAt: "Aug 28, 2025", ticketCount: 134 },
    { id: "e-3", fileName: "globex_results.xlsx", format: "xlsx", createdAt: "Aug 25, 2025", ticketCount: 87 },
  ],
};