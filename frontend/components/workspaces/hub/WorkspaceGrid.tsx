import type { Workspace } from "@/lib/api/workspaces";

import { WorkspaceCard } from "./WorkspaceCard";

interface WorkspaceGridProps {
  workspaces: Workspace[];
  deletingWorkspaceId: string | null;
  onOpen: (workspaceId: string) => void;
  onDelete: (workspace: Workspace) => void;
}

export function WorkspaceGrid({
  workspaces,
  deletingWorkspaceId,
  onOpen,
  onDelete,
}: WorkspaceGridProps) {
  return (
    <>
      <div className="mb-4">
        <p className="text-sm text-slate-500">
          {workspaces.length}{" "}
          {workspaces.length === 1
            ? "workspace"
            : "workspaces"}
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        {workspaces.map((workspace) => (
          <WorkspaceCard
            key={workspace.id}
            workspace={workspace}
            isDeleting={
              deletingWorkspaceId === workspace.id
            }
            onOpen={onOpen}
            onDelete={onDelete}
          />
        ))}
      </div>
    </>
  );
}