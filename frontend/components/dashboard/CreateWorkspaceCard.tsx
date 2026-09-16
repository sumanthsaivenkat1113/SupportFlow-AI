"use client";

import { Plus, Briefcase } from "lucide-react";

interface CreateWorkspaceCardProps {
  onCreateWorkspace?: () => void;
}

export function CreateWorkspaceCard({ onCreateWorkspace }: CreateWorkspaceCardProps) {
  return (
    <div className="rounded-xl border border-white/5 bg-[#131A2B] p-5">
      <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-600/10 text-indigo-400">
        <Briefcase size={20} />
      </div>
      <h3 className="text-sm font-semibold text-white">Create New Workspace</h3>
      <p className="mt-1 text-xs leading-relaxed text-slate-400">
        Upload your company docs and customer tickets to get started.
      </p>
      <button 
        onClick={onCreateWorkspace}
        className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 py-2 text-xs font-medium text-white transition-colors hover:bg-indigo-500"
      >
        <Plus size={14} /> Create Workspace
      </button>
    </div>
  );
}