// lib/api/workspaces.ts
import {
  ChunkingStrategy,
  CreateWorkspaceResponse,
  UploadTicketsResponse,
  TicketNormalizationResponse,
  TicketResolutionResponse
} from "@/types/workspace";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

if (!API_BASE_URL) {
  console.warn("NEXT_PUBLIC_API_URL is not defined");
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = "An error occurred";
    try {
      const errorData = await response.json();
      errorMessage = errorData.message || errorData.error || errorMessage;
    } catch {
      if (response.status === 401) errorMessage = "Your session expired. Please sign in again.";
      else if (response.status === 413) errorMessage = "The uploaded file is too large.";
      else if (response.status === 422) errorMessage = "Validation failed.";
      else errorMessage = `Request failed with status ${response.status}`;
    }
    throw new ApiError(response.status, errorMessage);
  }
  return response.json();
}

export async function createWorkspace({
  workspaceName,
  pdfFiles,
  chunkingStrategy,
  token, // Now strictly required
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

  if (!API_BASE_URL) throw new Error("API URL is not configured");

  const response = await fetch(`${API_BASE_URL}/api/workspaces`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
    },
    body: formData,
  });

  return handleResponse<CreateWorkspaceResponse>(response);
}

export async function uploadCustomerTickets({
  workspaceId,
  ticketFile,
  token, // Now strictly required
}: {
  workspaceId: string;
  ticketFile: File;
  token: string;
}): Promise<UploadTicketsResponse> {
  const formData = new FormData();
  formData.append("customer_tickets_file", ticketFile);

  if (!API_BASE_URL) throw new Error("API URL is not configured");

  const response = await fetch(
    `${API_BASE_URL}/api/workspaces/${workspaceId}/ticket-imports`,
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
      body: formData,
    }
  );

  return handleResponse<UploadTicketsResponse>(response);
}


// Ticket Normalization

export async function ticketNormalization({
  workspaceId,
  token,
}: {
  workspaceId: string;
  token: string;
}
) {
  if (!API_BASE_URL) throw new Error("API URL is not configured");
  const response = await fetch(
    `${API_BASE_URL}/workspaces/${workspaceId}/tickets-normalization`,
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
      body: workspaceId,
    }
  );
  return handleResponse<TicketNormalizationResponse>(response);
}



// Ticket Resolution

export async function ticketResolution({
  workspaceId,
  token,
}: {
  workspaceId: string;
  token: string;
}) { 
  if (!API_BASE_URL) throw new Error("API URL is not configured");
  const response = await fetch(
    `${API_BASE_URL}/workspaces/${workspaceId}/ticket-resolutions`,
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
      body: workspaceId,
    }
  );
  return handleResponse<TicketResolutionResponse>(response);
}