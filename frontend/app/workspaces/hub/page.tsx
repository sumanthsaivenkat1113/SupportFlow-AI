"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { Loader2, RefreshCw, Sparkles } from "lucide-react";

import { DashboardSidebar } from "@/components/dashboard/DashboardSidebar";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";

import {
  deleteWorkspace,
  getWorkspaces,
  type Workspace,
} from "@/lib/api/workspaces";

import { WorkspaceGrid } from "@/components/workspaces/hub/WorkspaceGrid";
import { WorkspaceEmpty } from "@/components/workspaces/hub/WorkspaceEmpty";
import { DeleteWorkspaceDialog } from "@/components/workspaces/hub/DeleteWorkspaceDialog";

export default function WorkspacesHubPage() {
  const router = useRouter();
  const { getToken, isLoaded } = useAuth();

  // ---------------------------------------------------------------------------
  // State
  // ---------------------------------------------------------------------------

  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);

  const [isLoading, setIsLoading] = useState(true);

  const [deletingWorkspaceId, setDeletingWorkspaceId] =
    useState<string | null>(null);

  const [workspaceToDelete, setWorkspaceToDelete] =
    useState<Workspace | null>(null);

  const [error, setError] = useState<string | null>(null);

  // ---------------------------------------------------------------------------
  // Load workspaces
  // ---------------------------------------------------------------------------

  const loadWorkspaces = useCallback(async () => {
    if (!isLoaded) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const token = await getToken();

      if (!token) {
        throw new Error(
          "Authentication token is missing. Please sign in again."
        );
      }

      const response = await getWorkspaces(token);

      if (!response.success) {
        throw new Error("Failed to load workspaces.");
      }

      setWorkspaces(response.workspaces);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong while loading workspaces."
      );
    } finally {
      setIsLoading(false);
    }
  }, [getToken, isLoaded]);

  // ---------------------------------------------------------------------------
  // Initial load
  // ---------------------------------------------------------------------------

  useEffect(() => {
    loadWorkspaces();
  }, [loadWorkspaces]);

  // ---------------------------------------------------------------------------
  // Open workspace
  // ---------------------------------------------------------------------------

  const handleWorkspaceClick = (workspaceId: string) => {
    router.push(`/workspaces/${workspaceId}/export`);
  };

  // ---------------------------------------------------------------------------
  // Open delete dialog
  // ---------------------------------------------------------------------------

  const handleOpenDeleteDialog = (workspace: Workspace) => {
    if (deletingWorkspaceId) {
      return;
    }

    setWorkspaceToDelete(workspace);
  };

  // ---------------------------------------------------------------------------
  // Close delete dialog
  // ---------------------------------------------------------------------------

  const handleCloseDeleteDialog = () => {
    if (deletingWorkspaceId) {
      return;
    }

    setWorkspaceToDelete(null);
  };

  // ---------------------------------------------------------------------------
  // Confirm delete workspace
  // ---------------------------------------------------------------------------

  const handleConfirmDelete = useCallback(async () => {
    if (!workspaceToDelete) {
      return;
    }

    const workspace = workspaceToDelete;

    setDeletingWorkspaceId(workspace.id);
    setError(null);

    try {
      const token = await getToken();

      if (!token) {
        throw new Error(
          "Authentication token is missing. Please sign in again."
        );
      }

      await deleteWorkspace(workspace.id, token);

      // Remove deleted workspace from UI immediately
      setWorkspaces((current) =>
        current.filter(
          (item) => item.id !== workspace.id
        )
      );

      // Close dialog
      setWorkspaceToDelete(null);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to delete workspace."
      );
    } finally {
      setDeletingWorkspaceId(null);
    }
  }, [getToken, workspaceToDelete]);

  // ---------------------------------------------------------------------------
  // Loading state
  // ---------------------------------------------------------------------------

  if (!isLoaded || isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#0B0F19]">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-400" />

          <p className="text-sm text-slate-500">
            Loading workspaces...
          </p>
        </div>
      </div>
    );
  }

  // ---------------------------------------------------------------------------
  // Page
  // ---------------------------------------------------------------------------

  return (
    <div className="min-h-screen bg-[#0B0F19] text-slate-200">
      {/* ------------------------------------------------------------------- */}
      {/* Sidebar                                                             */}
      {/* ------------------------------------------------------------------- */}

      <DashboardSidebar />

      {/* ------------------------------------------------------------------- */}
      {/* Main content                                                        */}
      {/* ------------------------------------------------------------------- */}

      <div className="lg:pl-64">
        <DashboardHeader />

        <main className="mx-auto max-w-7xl p-6">
          {/* ---------------------------------------------------------------- */}
          {/* Page header                                                      */}
          {/* ---------------------------------------------------------------- */}

          <div className="mb-8 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
            <div>
              {/* Badge */}

              <div
                className="
                  mb-3
                  inline-flex
                  items-center
                  gap-2
                  rounded-full
                  border
                  border-indigo-500/20
                  bg-indigo-500/10
                  px-3
                  py-1
                  text-xs
                  font-medium
                  text-indigo-400
                "
              >
                <Sparkles className="h-3.5 w-3.5" />

                Workspace Hub
              </div>

              {/* Title */}

              <h1 className="text-3xl font-bold tracking-tight text-white">
                Workspaces
              </h1>

              {/* Description */}

              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                Select a workspace to view and export its
                processed ticket resolutions.
              </p>
            </div>

            {/* Refresh */}

            <button
              type="button"
              onClick={loadWorkspaces}
              disabled={isLoading}
              className="
                inline-flex
                items-center
                justify-center
                gap-2
                rounded-lg
                border
                border-white/10
                bg-white/[0.03]
                px-4
                py-2.5
                text-sm
                font-medium
                text-slate-300
                transition
                hover:bg-white/[0.06]
                hover:text-white
                disabled:cursor-not-allowed
                disabled:opacity-50
              "
            >
              <RefreshCw className="h-4 w-4" />

              Refresh
            </button>
          </div>

          {/* ---------------------------------------------------------------- */}
          {/* Error message                                                    */}
          {/* ---------------------------------------------------------------- */}

          {error && (
            <div
              className="
                mb-6
                rounded-xl
                border
                border-red-500/20
                bg-red-500/10
                p-4
              "
            >
              <div className="flex items-center justify-between gap-4">
                <p className="text-sm text-red-400">
                  {error}
                </p>

                <button
                  type="button"
                  onClick={loadWorkspaces}
                  className="
                    text-xs
                    font-medium
                    text-red-300
                    transition-colors
                    hover:text-red-200
                  "
                >
                  Try again
                </button>
              </div>
            </div>
          )}

          {/* ---------------------------------------------------------------- */}
          {/* Workspace content                                                */}
          {/* ---------------------------------------------------------------- */}

          {!error && workspaces.length === 0 ? (
            <WorkspaceEmpty
              onCreate={() =>
                router.push("/workspaces/create")
              }
            />
          ) : (
            <WorkspaceGrid
              workspaces={workspaces}
              deletingWorkspaceId={deletingWorkspaceId}
              onOpen={handleWorkspaceClick}
              onDelete={handleOpenDeleteDialog}
            />
          )}
        </main>
      </div>

      {/* ------------------------------------------------------------------- */}
      {/* Delete confirmation dialog                                          */}
      {/* ------------------------------------------------------------------- */}

      <DeleteWorkspaceDialog
        workspace={workspaceToDelete}
        isDeleting={deletingWorkspaceId !== null}
        onClose={handleCloseDeleteDialog}
        onConfirm={handleConfirmDelete}
      />
    </div>
  );
}