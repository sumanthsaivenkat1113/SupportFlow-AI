"use client";

import Link from "next/link";
import { ExternalLink, Building2 } from "lucide-react";
import { Workspace } from "@/types/dashboard";

interface YourWorkspacesProps {
  workspaces: Workspace[];
  viewAllHref?: string; // Changed from onViewAll callback to href
}

export function YourWorkspaces({ workspaces, viewAllHref = "/workspaces" }: YourWorkspacesProps) {
  return (
    <div className="rounded-xl border border-white/5 bg-[#131A2B] p-5">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-200">Your Workspaces</h3>
        <Link 
          href={viewAllHref} 
          className="text-xs font-medium text-indigo-400 hover:text-indigo-300 transition-colors"
        >
          View all →
        </Link>
      </div>

      <div className="space-y-1">
        {workspaces.map((ws) => (
          <Link 
            key={ws.id} 
            href={`/workspaces/${ws.id}`}
            className="group flex items-center justify-between rounded-lg p-2.5 transition-colors hover:bg-white/5"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-white/5 text-slate-400 group-hover:text-slate-200 transition-colors">
                <Building2 size={16} />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-200">{ws.name}</p>
                <p className="text-[11px] text-slate-500">
                  {ws.documentCount} docs • {ws.ticketCount} tickets
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <span className="flex items-center gap-1.5 text-[10px] font-medium text-emerald-400">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                Active
              </span>
              <ExternalLink size={12} className="text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}