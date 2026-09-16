// types/dashboard.ts

export type TicketStatus = "automated" | "human-review" | "failed";
export type CategoryType = "Account" | "Billing" | "Technical" | "General";
export type ExportFormat = "json" | "csv" | "xlsx";
export type WorkspaceStatus = "active" | "inactive";

export interface User {
  name: string;
  organization?: string;
  avatarUrl?: string;
}

export interface MetricData {
  title: string;
  value: string | number;
  change?: {
    value: string;
    direction: "up" | "down";
  };
  description?: string;
  variant?: "blue" | "purple" | "green" | "orange";
}

export interface WorkflowStep {
  id: number;
  title: string;
  subtitle: string;
  icon: string; // We'll map this to Lucide icons in the component
}

export interface Ticket {
  id: string;
  customer: string;
  subject: string;
  category: CategoryType;
  status: TicketStatus;
  resolution?: string;
  createdAt: string;
}

export interface WorkspaceTickets {
  workspaceId: string;
  workspaceName: string;
  tickets: Ticket[];
}

export interface Workspace {
  id: string;
  name: string;
  documentCount: number;
  ticketCount: number;
  status: WorkspaceStatus;
}

export interface ExportFile {
  id: string;
  fileName: string;
  format: ExportFormat;
  createdAt: string;
  ticketCount: number;
  downloadUrl?: string;
}

export interface DashboardData {
  user: User;
  metrics: MetricData[];
  workflowSteps: WorkflowStep[];
  recentTickets: WorkspaceTickets[];
  workspaces: Workspace[];
  exports: ExportFile[];
}