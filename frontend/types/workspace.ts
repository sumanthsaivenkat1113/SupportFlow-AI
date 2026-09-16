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