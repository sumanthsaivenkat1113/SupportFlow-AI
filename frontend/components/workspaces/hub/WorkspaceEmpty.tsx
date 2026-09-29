import { FolderKanban } from "lucide-react";

interface WorkspaceEmptyProps {
  onCreate: () => void;
}

export function WorkspaceEmpty({
  onCreate,
}: WorkspaceEmptyProps) {
  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center rounded-2xl border border-dashed border-white/10 bg-white/[0.02] px-6 text-center">
      <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-500/10 text-indigo-400">
        <FolderKanban className="h-7 w-7" />
      </div>

      <h2 className="text-lg font-semibold text-white">
        No workspaces yet
      </h2>

      <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
        Create a workspace and upload your company
        documents and customer tickets to get started.
      </p>

      <button
        type="button"
        onClick={onCreate}
        className="
          mt-5
          rounded-lg
          bg-indigo-600
          px-4
          py-2.5
          text-sm
          font-medium
          text-white
          transition-colors
          hover:bg-indigo-500
        "
      >
        Create Workspace
      </button>
    </div>
  );
}