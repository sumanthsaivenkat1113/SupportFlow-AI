import {
  ArrowRight,
  FileText,
  FolderKanban,
  Loader2,
  Sparkles,
  Trash2,
} from "lucide-react";

import type { Workspace } from "@/lib/api/workspaces";

import { formatDate } from "@/lib/utils";

interface WorkspaceCardProps {
  workspace: Workspace;
  isDeleting: boolean;
  onOpen: (workspaceId: string) => void;
  onDelete: (workspace: Workspace) => void;
}

export function WorkspaceCard({
  workspace,
  isDeleting,
  onOpen,
  onDelete,
}: WorkspaceCardProps) {
  return (
    <div
      className="
        group
        relative
        overflow-hidden
        rounded-2xl
        border
        border-white/[0.07]
        bg-[#101725]
        p-5
        transition-all
        duration-200
        hover:-translate-y-0.5
        hover:border-indigo-500/30
        hover:bg-[#121A2A]
        hover:shadow-xl
        hover:shadow-indigo-950/20
      "
    >
      {/* ------------------------------------------------------------------ */}
      {/* Top accent                                                         */}
      {/* ------------------------------------------------------------------ */}

      <div
        className="
          absolute
          inset-x-0
          top-0
          h-px
          bg-gradient-to-r
          from-transparent
          via-indigo-500/50
          to-transparent
          opacity-0
          transition-opacity
          group-hover:opacity-100
        "
      />

      {/* ------------------------------------------------------------------ */}
      {/* Header                                                             */}
      {/* ------------------------------------------------------------------ */}

      <div className="mb-5 flex items-start justify-between">
        {/* Workspace icon */}

        <div
          className="
            flex
            h-11
            w-11
            items-center
            justify-center
            rounded-xl
            bg-indigo-500/10
            text-indigo-400
          "
        >
          <FolderKanban className="h-5 w-5" />
        </div>

        {/* Actions */}

        <div className="flex items-center gap-2">
          {/* Open workspace */}

          <button
            type="button"
            onClick={() => onOpen(workspace.id)}
            disabled={isDeleting}
            title="Open workspace"
            aria-label={`Open ${workspace.name}`}
            className="
              flex
              h-8
              w-8
              items-center
              justify-center
              rounded-lg
              text-slate-600
              transition-colors
              hover:bg-indigo-500/10
              hover:text-indigo-400
              disabled:cursor-not-allowed
              disabled:opacity-50
            "
          >
            <ArrowRight className="h-4 w-4" />
          </button>

          {/* Delete workspace */}

          <button
            type="button"
            onClick={() => onDelete(workspace)}
            disabled={isDeleting}
            title="Delete workspace"
            aria-label={`Delete ${workspace.name}`}
            className="
              flex
              h-8
              w-8
              items-center
              justify-center
              rounded-lg
              text-slate-600
              transition-colors
              hover:bg-red-500/10
              hover:text-red-400
              disabled:cursor-not-allowed
              disabled:opacity-50
            "
          >
            {isDeleting ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Trash2 className="h-4 w-4" />
            )}
          </button>
        </div>
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* Workspace information                                             */}
      {/* ------------------------------------------------------------------ */}

      <button
        type="button"
        onClick={() => onOpen(workspace.id)}
        disabled={isDeleting}
        className="
          block
          w-full
          text-left
          disabled:cursor-not-allowed
        "
      >
        <h2
          className="
            truncate
            text-base
            font-semibold
            text-white
            transition-colors
            group-hover:text-indigo-100
          "
        >
          {workspace.name}
        </h2>

        <p className="mt-1 truncate text-xs text-slate-600">
          {workspace.id}
        </p>
      </button>

      {/* ------------------------------------------------------------------ */}
      {/* Stats                                                              */}
      {/* ------------------------------------------------------------------ */}

      <div className="mt-6 grid grid-cols-2 gap-3">
        <Stat
          icon={<FileText className="h-4 w-4" />}
          label="Documents"
          value={workspace.total_documents}
        />

        <Stat
          icon={<Sparkles className="h-4 w-4" />}
          label="Chunks"
          value={workspace.total_chunks}
        />
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* Documents                                                          */}
      {/* ------------------------------------------------------------------ */}

      {workspace.documents.length > 0 && (
        <div className="mt-4 border-t border-white/[0.05] pt-4">
          <p
            className="
              mb-2
              text-[11px]
              font-medium
              uppercase
              tracking-wider
              text-slate-600
            "
          >
            Documents
          </p>

          <div className="space-y-2">
            {workspace.documents.slice(0, 2).map((document) => (
              <div
                key={document.id}
                className="flex min-w-0 items-center gap-2"
              >
                {/* Document icon */}

                <FileText className="h-3.5 w-3.5 shrink-0 text-slate-600" />

                {/* File name */}

                <span className="min-w-0 truncate text-xs text-slate-500">
                  {document.file_name}
                </span>

                {/* Status */}

                <span
                  className={`
                    ml-auto
                    shrink-0
                    rounded-full
                    px-2
                    py-0.5
                    text-[10px]
                    font-medium
                    ${
                      document.status === "completed"
                        ? "bg-emerald-500/10 text-emerald-400"
                        : "bg-amber-500/10 text-amber-400"
                    }
                  `}
                >
                  {document.status}
                </span>
              </div>
            ))}

            {/* Additional documents */}

            {workspace.documents.length > 2 && (
              <p className="text-[11px] text-slate-600">
                + {workspace.documents.length - 2} more
              </p>
            )}
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------ */}
      {/* Footer                                                             */}
      {/* ------------------------------------------------------------------ */}

      <div
        className="
          mt-5
          flex
          items-center
          justify-between
          border-t
          border-white/[0.05]
          pt-4
        "
      >
        {/* Created date */}

        <span className="text-xs text-slate-600">
          Created {formatDate(workspace.created_at)}
        </span>

        {/* Export page */}

        <button
          type="button"
          onClick={() => onOpen(workspace.id)}
          disabled={isDeleting}
          className="
            text-xs
            font-medium
            text-indigo-400
            transition-colors
            hover:text-indigo-300
            disabled:cursor-not-allowed
            disabled:opacity-50
          "
        >
          View exports →
        </button>
      </div>
    </div>
  );
}

// -----------------------------------------------------------------------------
// Stat component
// -----------------------------------------------------------------------------

interface StatProps {
  icon: React.ReactNode;
  label: string;
  value: number;
}

function Stat({
  icon,
  label,
  value,
}: StatProps) {
  return (
    <div
      className="
        rounded-xl
        border
        border-white/[0.05]
        bg-black/10
        p-3
      "
    >
      <div className="flex items-center gap-2 text-slate-500">
        {icon}

        <span className="text-xs">
          {label}
        </span>
      </div>

      <p className="mt-2 text-lg font-semibold text-slate-200">
        {value}
      </p>
    </div>
  );
}