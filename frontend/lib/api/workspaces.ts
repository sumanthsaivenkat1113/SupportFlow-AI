// lib/api/workspaces.ts
import {
  ChunkingStrategy,
  CreateWorkspaceResponse,
  UploadTicketsResponse,
  TicketNormalizationResponse,
  TicketResolutionResponse,
} from "@/types/workspace";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

if (!process.env.NEXT_PUBLIC_API_URL) {
  console.warn(
    "NEXT_PUBLIC_API_URL is not defined — falling back to http://localhost:8000"
  );
}

// -----------------------------------------------------------------------------
// Error handling
// -----------------------------------------------------------------------------

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function extractErrorMessage(
  response: Response,
  fallback: string
): Promise<string> {
  try {
    const data = await response.json();

    if (typeof data?.detail === "string") return data.detail;
    if (typeof data?.message === "string") return data.message;
    if (typeof data?.error === "string") return data.error;
  } catch {
    // Non-JSON body — fall through.
  }

  if (response.status === 401) {
    return "Your session expired. Please sign in again.";
  }

  if (response.status === 413) {
    return "The uploaded file is too large.";
  }

  if (response.status === 422) {
    return "Validation failed.";
  }

  return `${fallback} (HTTP ${response.status})`;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new ApiError(
      response.status,
      await extractErrorMessage(response, "An error occurred")
    );
  }

  // Some endpoints return 204 No Content — handle gracefully.
  if (response.status === 204) {
    return {} as T;
  }

  const text = await response.text();

  if (!text) {
    return {} as T;
  }

  try {
    return JSON.parse(text) as T;
  } catch {
    throw new ApiError(
      response.status,
      "Received an invalid response from the server."
    );
  }
}

// -----------------------------------------------------------------------------
// Create Workspace
// POST /api/workspaces
// -----------------------------------------------------------------------------

export async function createWorkspace({
  workspaceName,
  pdfFiles,
  chunkingStrategy,
  token,
}: {
  workspaceName: string;
  pdfFiles: File[];
  chunkingStrategy: ChunkingStrategy;
  token: string;
}): Promise<CreateWorkspaceResponse> {
  const formData = new FormData();
  formData.append("workspace_name", workspaceName.trim());
  formData.append("chunking_strategy", chunkingStrategy);
  pdfFiles.forEach((file) => formData.append("pdf_files", file));

  const response = await fetch(`${API_BASE_URL}/api/workspaces`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  return handleResponse<CreateWorkspaceResponse>(response);
}

// -----------------------------------------------------------------------------
// Upload Customer Tickets
// POST /api/workspaces/:workspaceId/ticket-imports
// -----------------------------------------------------------------------------

export async function uploadCustomerTickets({
  workspaceId,
  ticketFile,
  token,
}: {
  workspaceId: string;
  ticketFile: File;
  token: string;
}): Promise<UploadTicketsResponse> {
  const formData = new FormData();
  formData.append("customer_tickets_file", ticketFile);

  const response = await fetch(
    `${API_BASE_URL}/api/workspaces/${encodeURIComponent(
      workspaceId
    )}/ticket-imports`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    }
  );

  return handleResponse<UploadTicketsResponse>(response);
}

// -----------------------------------------------------------------------------
// Ticket Normalization
// POST /workspaces/:workspaceId/tickets-normalization
// -----------------------------------------------------------------------------

export async function ticketNormalization({
  workspaceId,
  token,
}: {
  workspaceId: string;
  token: string;
}): Promise<TicketNormalizationResponse> {
  const response = await fetch(
    `${API_BASE_URL}/workspaces/${encodeURIComponent(
      workspaceId
    )}/tickets-normalization`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return handleResponse<TicketNormalizationResponse>(response);
}

// -----------------------------------------------------------------------------
// Ticket Resolution
// POST /workspaces/:workspaceId/ticket-resolutions
// -----------------------------------------------------------------------------

export async function ticketResolution({
  workspaceId,
  token,
}: {
  workspaceId: string;
  token: string;
}): Promise<TicketResolutionResponse> {
  const response = await fetch(
    `${API_BASE_URL}/workspaces/${encodeURIComponent(
      workspaceId
    )}/ticket-resolutions`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return handleResponse<TicketResolutionResponse>(response);
}

// -----------------------------------------------------------------------------
// Workspace HUB — Types
// -----------------------------------------------------------------------------

export type WorkspaceDocumentStatus =
  | "pending"
  | "processing"
  | "completed"
  | "failed"
  | string;

export interface WorkspaceDocument {
  id: string;
  file_name: string;
  status: WorkspaceDocumentStatus;
}

export interface Workspace {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
  total_documents: number;
  total_chunks: number;
  documents: WorkspaceDocument[];
}

export interface GetWorkspacesResponse {
  success: boolean;
  total_workspaces: number;
  workspaces: Workspace[];
}

export interface DeleteWorkspaceResponse {
  success: boolean;
  message?: string;
}

// -----------------------------------------------------------------------------
// GET /api/workspaces
// -----------------------------------------------------------------------------

export async function getWorkspaces(
  token: string
): Promise<GetWorkspacesResponse> {
  if (!token) {
    throw new Error("Authentication token is missing.");
  }

  const response = await fetch(`${API_BASE_URL}/api/workspaces`, {
    method: "GET",
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new ApiError(
      response.status,
      await extractErrorMessage(response, "Failed to fetch workspaces.")
    );
  }

  const data = await response.json();

  // Normalize: support both `{ success, workspaces }` and a bare array.
  if (Array.isArray(data)) {
    return {
      success: true,
      total_workspaces: data.length,
      workspaces: data as Workspace[],
    };
  }

  return {
    success: data.success ?? true,
    total_workspaces:
      data.total_workspaces ?? data.workspaces?.length ?? 0,
    workspaces: (data.workspaces ?? []) as Workspace[],
  };
}

// -----------------------------------------------------------------------------
// DELETE /api/workspaces/:workspaceId
// -----------------------------------------------------------------------------

export async function deleteWorkspace(
  workspaceId: string,
  token: string
): Promise<DeleteWorkspaceResponse> {
  if (!workspaceId) {
    throw new Error("Workspace ID is required.");
  }

  if (!token) {
    throw new Error("Authentication token is missing.");
  }

  const response = await fetch(
    `${API_BASE_URL}/api/workspaces/${encodeURIComponent(workspaceId)}`,
    {
      method: "DELETE",
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    throw new ApiError(
      response.status,
      await extractErrorMessage(response, "Failed to delete workspace.")
    );
  }

  // Some backends return 204 No Content — handle that gracefully.
  if (response.status === 204) {
    return { success: true };
  }

  const text = await response.text();

  if (!text) {
    return { success: true };
  }

  try {
    const data = JSON.parse(text) as Partial<DeleteWorkspaceResponse>;

    return {
      success: data.success ?? true,
      message: data.message,
    };
  } catch {
    return { success: true };
  }
}