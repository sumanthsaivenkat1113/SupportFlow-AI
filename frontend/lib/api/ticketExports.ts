// lib/api/ticketExports.ts

export type TicketGeneratedType =
  | "ai-automated"
  | "human-required";

export type TicketExportFormat =
  | "json"
  | "csv"
  | "excel";

interface DownloadTicketExportParams {
  workspaceId: string;
  generated: TicketGeneratedType;
  format: TicketExportFormat;
  token: string;
}

interface DownloadTicketExportResult {
  blob: Blob;
  filename: string;
}

/**
 * Downloads ticket resolutions from the backend.
 *
 * Backend endpoint:
 *
 * GET /api/workspaces/{workspace_id}/ticket-resolutions/export
 *
 * Query params:
 *   generated = ai-automated | human-required
 *   format    = json | csv | excel
 */
export async function downloadTicketExport({
  workspaceId,
  generated,
  format,
  token,
}: DownloadTicketExportParams): Promise<DownloadTicketExportResult> {
  if (!workspaceId) {
    throw new Error("Workspace ID is required.");
  }

  if (!token) {
    throw new Error("Authentication token is missing.");
  }

  const params = new URLSearchParams({
    generated,
    format,
  });

  const baseUrl =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const url =
    `${baseUrl}/api/workspaces/${workspaceId}` +
    `/ticket-resolutions/export?${params.toString()}`;

  const response = await fetch(url, {
    method: "GET",
    headers: {
      Accept:
        format === "json"
          ? "application/json"
          : format === "csv"
            ? "text/csv"
            : "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    let errorMessage = "Failed to export ticket resolutions.";

    try {
      const contentType = response.headers.get("content-type") || "";

      if (contentType.includes("application/json")) {
        const errorData = await response.json();

        if (typeof errorData?.detail === "string") {
          errorMessage = errorData.detail;
        } else if (typeof errorData?.message === "string") {
          errorMessage = errorData.message;
        }
      } else {
        const text = await response.text();

        if (text) {
          errorMessage = text;
        }
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(errorMessage);
  }

  const blob = await response.blob();

  if (blob.size === 0) {
    throw new Error("The exported file is empty.");
  }

  const contentDisposition =
    response.headers.get("Content-Disposition");

  const filename = getFilenameFromContentDisposition(
    contentDisposition,
    workspaceId,
    generated,
    format
  );

  return {
    blob,
    filename,
  };
}

/**
 * Extract filename from:
 *
 * Content-Disposition:
 * attachment; filename="workspace_xxx_ai-automated_ticket_resolutions.csv"
 */
function getFilenameFromContentDisposition(
  contentDisposition: string | null,
  workspaceId: string,
  generated: TicketGeneratedType,
  format: TicketExportFormat
): string {
  if (contentDisposition) {
    // filename*=UTF-8''filename.ext
    const encodedMatch =
      contentDisposition.match(
        /filename\*=UTF-8''([^;]+)/i
      );

    if (encodedMatch?.[1]) {
      try {
        return decodeURIComponent(encodedMatch[1]);
      } catch {
        // Continue to normal filename parsing.
      }
    }

    // filename="filename.ext"
    const filenameMatch =
      contentDisposition.match(
        /filename="([^"]+)"/i
      );

    if (filenameMatch?.[1]) {
      return filenameMatch[1];
    }

    // filename=filename.ext
    const unquotedMatch =
      contentDisposition.match(
        /filename=([^;]+)/i
      );

    if (unquotedMatch?.[1]) {
      return unquotedMatch[1].trim();
    }
  }

  const extension =
    format === "excel"
      ? "xlsx"
      : format;

  return `workspace_${workspaceId}_${generated}_ticket_resolutions.${extension}`;
}

/**
 * Triggers a browser download.
 */
export function saveBlobAsFile(
  blob: Blob,
  filename: string
): void {
  const url = window.URL.createObjectURL(blob);

  const anchor = document.createElement("a");

  anchor.href = url;
  anchor.download = filename;

  document.body.appendChild(anchor);

  anchor.click();

  anchor.remove();

  // Give the browser time to start the download
  // before releasing the object URL.
  window.setTimeout(() => {
    window.URL.revokeObjectURL(url);
  }, 1000);
}