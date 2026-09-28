export type ChunkingStrategy =
  | "Semantic"
  | "token_based_500"
  | "Structure_aware";

export type WorkspacePdfResponse = {
  pdf_no: number;
  pdf_file_name: string;
};

export type CreateWorkspaceResponse = {
  success: boolean;
  message: string;
  workspace_id: string;
  workspace_name: string;
  pdf_files: WorkspacePdfResponse[];
  total_pdf_files: number;
  chunking_strategy: ChunkingStrategy;
  no_of_chunks: number;
};

export type UploadTicketsResponse = {
  success: boolean;
  message: string;
};

export interface WorkspaceFormData {
  workspaceName: string;
  pdfFiles: File[];
  chunkingStrategy: ChunkingStrategy;
}

export interface TicketFormData {
  ticketFile: File | null;
}


export type NormalizedTicket = {
  ticket_id: string;
  description: string;
};

export type TicketNormalizationResponse = {
  success: boolean;
  ticket_normalization_id: string;
  total_tickets: number;
  normalized_tickets: NormalizedTicket[];
  time_execution: number | null;
};


export type TicketResolutionResponse = {
  success: boolean;
  workspace_id: string; 
  total_tickets: number;
  total_batches: number;
  batch_size: number;
  resolutions: Record<string, any>[];
  time_execution: number | null;
};