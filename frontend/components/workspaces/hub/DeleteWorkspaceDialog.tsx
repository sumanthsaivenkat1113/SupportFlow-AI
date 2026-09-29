"use client";

import { AlertTriangle, Loader2, Trash2, X } from "lucide-react";

import type { Workspace } from "@/lib/api/workspaces";

interface DeleteWorkspaceDialogProps {
  workspace: Workspace | null;
  isDeleting: boolean;
  onClose: () => void;
  onConfirm: () => void;
}

export function DeleteWorkspaceDialog({
  workspace,
  isDeleting,
  onClose,
  onConfirm,
}: DeleteWorkspaceDialogProps) {
  if (!workspace) {
    return null;
  }

  return (
    <div
      className="
        fixed
        inset-0
        z-50
        flex
        items-center
        justify-center
        bg-black/70
        p-4
        backdrop-blur-sm
      "
      onMouseDown={(event) => {
        if (event.target === event.currentTarget && !isDeleting) {
          onClose();
        }
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="delete-workspace-title"
        className="
          w-full
          max-w-md
          overflow-hidden
          rounded-2xl
          border
          border-white/[0.08]
          bg-[#101725]
          shadow-2xl
          shadow-black/40
        "
      >
        {/* Header */}

        <div className="flex items-start justify-between px-6 pt-6">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-red-500/10 text-red-400">
            <Trash2 className="h-5 w-5" />
          </div>

          <button
            type="button"
            onClick={onClose}
            disabled={isDeleting}
            aria-label="Close"
            className="
              flex
              h-8
              w-8
              items-center
              justify-center
              rounded-lg
              text-slate-500
              transition-colors
              hover:bg-white/5
              hover:text-slate-300
              disabled:cursor-not-allowed
              disabled:opacity-50
            "
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Content */}

        <div className="px-6 pb-6 pt-5">
          <h2
            id="delete-workspace-title"
            className="text-lg font-semibold text-white"
          >
            Delete workspace?
          </h2>

          <p className="mt-2 text-sm leading-6 text-slate-400">
            Are you sure you want to delete{" "}
            <span className="font-medium text-slate-200">
              "{workspace.name}"
            </span>
            ?
          </p>

          {/* Warning */}

          <div className="mt-5 flex gap-3 rounded-xl border border-red-500/10 bg-red-500/[0.06] p-3.5">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-red-400" />

            <div>
              <p className="text-xs font-medium text-red-300">
                This action cannot be undone.
              </p>

              <p className="mt-1 text-xs leading-5 text-slate-500">
                The workspace and its associated data will be
                permanently deleted.
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}

        <div className="flex items-center justify-end gap-3 border-t border-white/[0.06] bg-black/10 px-6 py-4">
          <button
            type="button"
            onClick={onClose}
            disabled={isDeleting}
            className="
              rounded-lg
              border
              border-white/10
              bg-white/[0.03]
              px-4
              py-2
              text-sm
              font-medium
              text-slate-300
              transition-colors
              hover:bg-white/[0.06]
              hover:text-white
              disabled:cursor-not-allowed
              disabled:opacity-50
            "
          >
            Cancel
          </button>

          <button
            type="button"
            onClick={onConfirm}
            disabled={isDeleting}
            className="
              inline-flex
              min-w-[90px]
              items-center
              justify-center
              gap-2
              rounded-lg
              bg-red-600
              px-4
              py-2
              text-sm
              font-medium
              text-white
              transition-colors
              hover:bg-red-500
              disabled:cursor-not-allowed
              disabled:opacity-60
            "
          >
            {isDeleting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Deleting
              </>
            ) : (
              <>
                <Trash2 className="h-4 w-4" />
                Delete
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}