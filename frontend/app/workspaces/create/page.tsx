// app/workspaces/create/page.tsx
"use client";

import React, { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useUser, useAuth } from "@clerk/nextjs";
import { ArrowLeft, ArrowRight, Loader2 } from "lucide-react";

// Dashboard Components
import { DashboardSidebar } from "@/components/dashboard/DashboardSidebar";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";

// Workspace Components
import { WorkspaceStepIndicator } from "@/components/workspaces/create/WorkspaceStepIndicator";
import { WorkspaceDocumentsStep } from "@/components/workspaces/create/WorkspaceDocumentsStep";
import { CustomerTicketsStep } from "@/components/workspaces/create/CustomerTicketsStep";
import { WorkspaceNextSteps } from "@/components/workspaces/create/WorkspaceNextSteps";
import { DataSafetyCard } from "@/components/workspaces/create/DataSafetyCard";

// API & Types
import {
  createWorkspace,
  uploadCustomerTickets,
  ticketNormalization,
  ticketResolution
} from "@/lib/api/workspaces";
import { ChunkingStrategy } from "@/types/workspace";

export default function CreateWorkspacePage() {
  const router = useRouter();
  const { isLoaded } = useUser();
  const { getToken } = useAuth();

  // ============================================================================
  // ⚠️ ALL HOOKS MUST BE DECLARED HERE, BEFORE ANY EARLY RETURNS
  // ============================================================================

  // Step state
  const [currentStep, setCurrentStep] = useState(1);
  const [workspaceId, setWorkspaceId] = useState<string | null>(null);

  // Step 1 state
  const [workspaceName, setWorkspaceName] = useState("");
  const [pdfFiles, setPdfFiles] = useState<File[]>([]);
  const [chunkingStrategy, setChunkingStrategy] = useState<ChunkingStrategy>("Semantic");

  // Step 2 state
  const [ticketFile, setTicketFile] = useState<File | null>(null);

  // Loading and error states
  const [isCreatingWorkspace, setIsCreatingWorkspace] = useState(false);
  const [isUploadingTickets, setIsUploadingTickets] = useState(false);
  const [workspaceError, setWorkspaceError] = useState<string | undefined>();
  const [ticketError, setTicketError] = useState<string | undefined>();

  // Validation
  const validateWorkspaceName = useCallback((): string | undefined => {
    const trimmed = workspaceName.trim();
    if (!trimmed) {
      return "Workspace name is required";
    }
    if (trimmed.length > 50) {
      return "Workspace name must be 50 characters or less";
    }
    return undefined;
  }, [workspaceName]);

  const validateStep1 = useCallback((): boolean => {
    const nameError = validateWorkspaceName();
    setWorkspaceError(nameError);

    if (nameError) return false;
    if (pdfFiles.length === 0) {
      setWorkspaceError("Please upload at least one PDF file");
      return false;
    }
    if (pdfFiles.length > 5) {
      setWorkspaceError("You can upload a maximum of 5 PDF files");
      return false;
    }

    return true;
  }, [validateWorkspaceName, pdfFiles]);

  const validateStep2 = useCallback((): boolean => {
    if (!ticketFile) {
      setTicketError("Please upload a tickets file");
      return false;
    }
    return true;
  }, [ticketFile]);

  // Step 1 submission
  const handleNextToStep2 = useCallback(async () => {
    if (!validateStep1()) return;

    setIsCreatingWorkspace(true);
    setWorkspaceError(undefined);

    try {
      // STRICT CHECK: Get the token and ensure it exists
      const token = await getToken();
      if (!token) {
        throw new Error("Authentication token is missing. Please sign in again.");
      }

      const response = await createWorkspace({
        workspaceName: workspaceName.trim(),
        pdfFiles,
        chunkingStrategy,
        token,
      });

      if (response.success && response.workspace_id) {
        setWorkspaceId(response.workspace_id);
        setCurrentStep(2);
      } else {
        setWorkspaceError(response.message || "Failed to create workspace");
      }
    } catch (error) {
      if (error instanceof Error) {
        setWorkspaceError(error.message);
      } else {
        setWorkspaceError("Something went wrong while creating the workspace");
      }
    } finally {
      setIsCreatingWorkspace(false);
    }
  }, [validateStep1, workspaceName, pdfFiles, chunkingStrategy, getToken]);

  // Step 2 submission
  const handleCreateWorkspace = useCallback(async () => {
    if (!validateStep2() || !workspaceId) return;

    setIsUploadingTickets(true);
    setTicketError(undefined);

    try {
      // STRICT CHECK: Get the token and ensure it exists
      const token = await getToken();
      if (!token) {
        throw new Error("Authentication token is missing. Please sign in again.");
      }

      await uploadCustomerTickets({
        workspaceId,
        ticketFile: ticketFile!,
        token,
      });

      // steps; ticket normalization and ticket resolution

      // Ticket Normalization

      await ticketNormalization({
        workspaceId,
        token
      })

      // Ticket Resolution

      await ticketResolution({
        workspaceId,
        token
      })


      // Success - navigate to workspaces page
      router.push(`/workspaces/${workspaceId}/export`);
    } catch (error) {
      if (error instanceof Error) {
        setTicketError(error.message);
      } else {
        setTicketError("The selected ticket file could not be processed");
      }
    } finally {
      setIsUploadingTickets(false);
    }
  }, [validateStep2, workspaceId, ticketFile, router, getToken]);

  // ============================================================================
  // ✅ NOW IT IS SAFE TO DO CONDITIONAL RETURNS
  // ============================================================================

  if (!isLoaded) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#0B0F19]">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
      </div>
    );
  }

  const steps = [
    { number: 1, label: "Workspace & Documents" },
    { number: 2, label: "Customer Tickets" },
  ];

  const isStep1Valid = workspaceName.trim().length > 0 && pdfFiles.length > 0;
  const isStep2Valid = ticketFile !== null;

  return (
    <div className="min-h-screen bg-[#0B0F19] text-slate-200">
      {/* Reused Sidebar */}
      <DashboardSidebar />

      {/* Main Layout Wrapper */}
      <div className="lg:pl-64">
        {/* Reused Header */}
        <DashboardHeader />

        <main className="mx-auto max-w-7xl p-6">
          {/* Page Header */}
          <div className="mb-8">
            <Link
              href="/workspaces"
              className="inline-flex items-center gap-2 text-[#6B7894] hover:text-[#F8FAFC] transition-colors mb-4"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Workspaces
            </Link>

            <div>
              <h1 className="text-3xl font-bold text-[#F8FAFC] mb-2">
                Create Workspace
              </h1>
              <p className="text-[#6B7894] max-w-2xl">
                Set up your workspace by providing a name, uploading company documents
                and customer tickets. We'll handle the rest with AI.
              </p>
            </div>
          </div>

          {/* Step Indicator */}
          <WorkspaceStepIndicator currentStep={currentStep} steps={steps} />

          {/* Main Content - Two Column Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Form Area */}
            <div className="lg:col-span-2 space-y-6">
              {/* Step 1 */}
              <div className={currentStep >= 1 ? "block" : "hidden"}>
                <WorkspaceDocumentsStep
                  workspaceName={workspaceName}
                  onWorkspaceNameChange={setWorkspaceName}
                  pdfFiles={pdfFiles}
                  onPdfFilesChange={setPdfFiles}
                  chunkingStrategy={chunkingStrategy}
                  onChunkingStrategyChange={setChunkingStrategy}
                  error={workspaceError}
                />

                {currentStep === 1 && (
                  <div className="flex justify-end mt-6">
                    <button
                      onClick={handleNextToStep2}
                      disabled={!isStep1Valid || isCreatingWorkspace}
                      className={`
                        inline-flex items-center gap-2 px-6 py-3 rounded-lg font-medium
                        transition-all duration-200
                        ${isStep1Valid && !isCreatingWorkspace
                          ? "bg-gradient-to-r from-[#635BFF] to-[#8B5CF6] text-white hover:from-[#554CF0] hover:to-[#7C4FE0] shadow-lg shadow-[#635BFF]/25"
                          : "bg-[#1D2942] text-[#6B7894] cursor-not-allowed"
                        }
                      `}
                    >
                      {isCreatingWorkspace ? (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin" />
                          Creating workspace...
                        </>
                      ) : (
                        <>
                          Next: Upload Tickets
                          <ArrowRight className="w-5 h-5" />
                        </>
                      )}
                    </button>
                  </div>
                )}
              </div>

              {/* Step 2 */}
              {currentStep === 2 && (
                <div className="animate-in fade-in slide-in-from-bottom-4 duration-300">
                  <CustomerTicketsStep
                    ticketFile={ticketFile}
                    onTicketFileChange={setTicketFile}
                    error={ticketError}
                  />

                  <div className="flex justify-end mt-6">
                    <button
                      onClick={handleCreateWorkspace}
                      disabled={!isStep2Valid || isUploadingTickets}
                      className={`
                        inline-flex items-center gap-2 px-6 py-3 rounded-lg font-medium
                        transition-all duration-200
                        ${isStep2Valid && !isUploadingTickets
                          ? "bg-gradient-to-r from-[#635BFF] to-[#8B5CF6] text-white hover:from-[#554CF0] hover:to-[#7C4FE0] shadow-lg shadow-[#635BFF]/25"
                          : "bg-[#1D2942] text-[#6B7894] cursor-not-allowed"
                        }
                      `}
                    >
                      {isUploadingTickets ? (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin" />
                          Uploading tickets...
                        </>
                      ) : (
                        "Create Workspace"
                      )}
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Right Sidebar Information Panel */}
            <div className="space-y-6">
              <WorkspaceNextSteps />
              <DataSafetyCard />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}