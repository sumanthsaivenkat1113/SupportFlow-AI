"use client";

import React, { useCallback, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import {
  ArrowLeft,
  CheckCircle2,
  Download,
  FileJson,
  FileSpreadsheet,
  FileText,
  Loader2,
} from "lucide-react";

import { DashboardSidebar } from "@/components/dashboard/DashboardSidebar";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";

import {
  downloadTicketExport,
  saveBlobAsFile,
  type TicketExportFormat,
  type TicketGeneratedType,
} from "@/lib/api/ticketExports";

type ExportType = {
  generated: TicketGeneratedType;
  title: string;
  description: string;
  icon: React.ReactNode;
};

const EXPORT_TYPES: ExportType[] = [
  {
    generated: "ai-automated",
    title: "AI Automated Tickets",
    description:
      "Tickets that were successfully resolved automatically by AI.",
    icon: (
      <CheckCircle2 className="h-6 w-6" />
    ),
  },
  {
    generated: "human-required",
    title: "Human Required Tickets",
    description:
      "Tickets that require human intervention or review.",
    icon: (
      <FileText className="h-6 w-6" />
    ),
  },
];

const FORMATS: {
  format: TicketExportFormat;
  label: string;
  description: string;
  extension: string;
  icon: React.ReactNode;
}[] = [
  {
    format: "json",
    label: "JSON",
    description: "Structured JSON data",
    extension: ".json",
    icon: (
      <FileJson className="h-5 w-5" />
    ),
  },
  {
    format: "csv",
    label: "CSV",
    description: "Spreadsheet-compatible data",
    extension: ".csv",
    icon: (
      <FileText className="h-5 w-5" />
    ),
  },
  {
    format: "excel",
    label: "Excel",
    description: "Microsoft Excel workbook",
    extension: ".xlsx",
    icon: (
      <FileSpreadsheet className="h-5 w-5" />
    ),
  },
];

export default function TicketExportPage() {
  const params = useParams();
  const { getToken, isLoaded } = useAuth();

  const workspaceId = params?.workspaceId as string;

  const [downloading, setDownloading] = useState<string | null>(
    null
  );

  const [successMessage, setSuccessMessage] =
    useState<string | null>(null);

  const [errorMessage, setErrorMessage] =
    useState<string | null>(null);

  const handleDownload = useCallback(
    async (
      generated: TicketGeneratedType,
      format: TicketExportFormat
    ) => {
      if (!workspaceId) {
        setErrorMessage("Workspace ID is missing.");
        return;
      }

      if (!isLoaded) {
        return;
      }

      const downloadKey = `${generated}-${format}`;

      setDownloading(downloadKey);
      setErrorMessage(null);
      setSuccessMessage(null);

      try {
        const token = await getToken();

        if (!token) {
          throw new Error(
            "Authentication token is missing. Please sign in again."
          );
        }

        const { blob, filename } =
          await downloadTicketExport({
            workspaceId,
            generated,
            format,
            token,
          });

        saveBlobAsFile(blob, filename);

        setSuccessMessage(
          `${format.toUpperCase()} export downloaded successfully.`
        );
      } catch (error) {
        if (error instanceof Error) {
          setErrorMessage(error.message);
        } else {
          setErrorMessage(
            "Something went wrong while exporting the tickets."
          );
        }
      } finally {
        setDownloading(null);
      }
    },
    [workspaceId, getToken, isLoaded]
  );

  if (!isLoaded) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#0B0F19]">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0B0F19] text-slate-200">
      {/* Sidebar */}
      <DashboardSidebar />

      {/* Main */}
      <div className="lg:pl-64">
        <DashboardHeader />

        <main className="mx-auto max-w-6xl p-6">
          {/* Back */}
          <Link
            href={`/workspaces/${workspaceId}`}
            className="mb-6 inline-flex items-center gap-2 text-sm text-[#6B7894] transition-colors hover:text-white"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Workspace
          </Link>

          {/* Header */}
          <div className="mb-10">
            <div className="mb-3 inline-flex items-center rounded-full border border-[#26324A] bg-[#111827] px-3 py-1 text-xs font-medium text-[#8B9BB8]">
              Ticket Exports
            </div>

            <h1 className="text-3xl font-bold tracking-tight text-[#F8FAFC]">
              Export Tickets
            </h1>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-[#6B7894]">
              Download your processed ticket resolutions in
              JSON, CSV, or Excel format.
            </p>
          </div>

          {/* Success */}
          {successMessage && (
            <div className="mb-6 flex items-center gap-3 rounded-xl border border-emerald-500/20 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-400">
              <CheckCircle2 className="h-5 w-5 shrink-0" />
              <span>{successMessage}</span>
            </div>
          )}

          {/* Error */}
          {errorMessage && (
            <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">
              {errorMessage}
            </div>
          )}

          {/* Export Sections */}
          <div className="space-y-6">
            {EXPORT_TYPES.map((exportType) => (
              <section
                key={exportType.generated}
                className="overflow-hidden rounded-2xl border border-[#1D2942] bg-[#101725]"
              >
                {/* Section Header */}
                <div className="border-b border-[#1D2942] px-6 py-5">
                  <div className="flex items-start gap-4">
                    <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[#635BFF]/10 text-[#8B7CFF]">
                      {exportType.icon}
                    </div>

                    <div>
                      <h2 className="text-lg font-semibold text-[#F8FAFC]">
                        {exportType.title}
                      </h2>

                      <p className="mt-1 text-sm text-[#6B7894]">
                        {exportType.description}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Formats */}
                <div className="grid grid-cols-1 gap-3 p-5 md:grid-cols-3">
                  {FORMATS.map((item) => {
                    const key = `${exportType.generated}-${item.format}`;

                    const isDownloading =
                      downloading === key;

                    return (
                      <button
                        key={item.format}
                        type="button"
                        onClick={() =>
                          handleDownload(
                            exportType.generated,
                            item.format
                          )
                        }
                        disabled={downloading !== null}
                        className="
                          group
                          flex
                          items-center
                          gap-4
                          rounded-xl
                          border
                          border-[#26324A]
                          bg-[#0B0F19]
                          p-4
                          text-left
                          transition-all
                          duration-200
                          hover:border-[#635BFF]/50
                          hover:bg-[#151C2B]
                          disabled:cursor-not-allowed
                          disabled:opacity-60
                        "
                      >
                        {/* Icon */}
                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#1A2235] text-[#8B7CFF] transition-colors group-hover:bg-[#635BFF]/10">
                          {isDownloading ? (
                            <Loader2 className="h-5 w-5 animate-spin" />
                          ) : (
                            item.icon
                          )}
                        </div>

                        {/* Text */}
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-semibold text-[#F8FAFC]">
                              {item.label}
                            </span>

                            <span className="text-xs text-[#526078]">
                              {item.extension}
                            </span>
                          </div>

                          <p className="mt-1 text-xs text-[#6B7894]">
                            {isDownloading
                              ? "Preparing download..."
                              : item.description}
                          </p>
                        </div>

                        {/* Download */}
                        {!isDownloading && (
                          <Download className="h-4 w-4 shrink-0 text-[#526078] transition-colors group-hover:text-[#8B7CFF]" />
                        )}
                      </button>
                    );
                  })}
                </div>
              </section>
            ))}
          </div>

          {/* Information */}
          <div className="mt-8 rounded-2xl border border-[#1D2942] bg-[#0F1522] p-5">
            <div className="flex gap-3">
              <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[#635BFF]/10 text-[#8B7CFF]">
                <Download className="h-4 w-4" />
              </div>

              <div>
                <h3 className="text-sm font-medium text-[#F8FAFC]">
                  About exports
                </h3>

                <p className="mt-1 text-xs leading-5 text-[#6B7894]">
                  Each download contains the ticket information,
                  generated response, classification, model name,
                  status, and creation timestamp returned by the
                  ticket resolution service.
                </p>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}