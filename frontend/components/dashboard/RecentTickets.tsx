"use client";

import { useState } from "react";
import { MoreHorizontal, ExternalLink } from "lucide-react";
import { WorkspaceTickets, TicketStatus, CategoryType } from "@/types/dashboard";
import { cn } from "@/lib/utils";

interface RecentTicketsProps {
  workspaces: WorkspaceTickets[];
  onViewAll?: () => void;
}

type FilterType = "all" | TicketStatus;

const filters: { label: string; value: FilterType; count?: number }[] = [
  { label: "All", value: "all" },
  { label: "Automated", value: "automated" },
  { label: "Human Review", value: "human-review" },
  { label: "Failed", value: "failed" },
];

const statusStyles: Record<TicketStatus, string> = {
  automated: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  "human-review": "bg-amber-500/10 text-amber-400 border-amber-500/20",
  failed: "bg-red-500/10 text-red-400 border-red-500/20",
};

const categoryStyles: Record<CategoryType, string> = {
  Account: "bg-blue-500/10 text-blue-400",
  Billing: "bg-purple-500/10 text-purple-400",
  Technical: "bg-cyan-500/10 text-cyan-400",
  General: "bg-slate-500/10 text-slate-400",
};

export function RecentTickets({ workspaces, onViewAll }: RecentTicketsProps) {
  const [activeFilter, setActiveFilter] = useState<FilterType>("all");

  const allTickets = workspaces.flatMap((ws) => ws.tickets);
  const filteredTickets = activeFilter === "all" 
    ? allTickets 
    : allTickets.filter((t) => t.status === activeFilter);

  return (
    <div className="rounded-xl border border-white/5 bg-[#131A2B]">
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/5 p-5">
        <h3 className="text-sm font-semibold text-slate-200">Recent Tickets</h3>
        <button onClick={onViewAll} className="flex items-center gap-1 text-xs font-medium text-indigo-400 hover:text-indigo-300 transition-colors">
          View all <ExternalLink size={12} />
        </button>
      </div>

      <div className="border-b border-white/5 px-5 pt-4">
        <div className="flex gap-1 overflow-x-auto pb-2 scrollbar-hide">
          {filters.map((f) => (
            <button
              key={f.value}
              onClick={() => setActiveFilter(f.value)}
              className={cn(
                "whitespace-nowrap rounded-full px-3 py-1.5 text-xs font-medium transition-colors",
                activeFilter === f.value
                  ? "bg-indigo-600 text-white"
                  : "bg-white/5 text-slate-400 hover:bg-white/10 hover:text-slate-200"
              )}
            >
              {f.label} {f.count !== undefined && `(${f.count})`}
            </button>
          ))}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-white/5 text-slate-500">
              <th className="px-5 py-3 font-medium"><input type="checkbox" className="rounded border-white/10 bg-white/5" /></th>
              <th className="px-5 py-3 font-medium">Ticket ID</th>
              <th className="px-5 py-3 font-medium">Customer</th>
              <th className="px-5 py-3 font-medium">Subject</th>
              <th className="px-5 py-3 font-medium">Category</th>
              <th className="px-5 py-3 font-medium">Status</th>
              <th className="px-5 py-3 font-medium">Resolution</th>
              <th className="px-5 py-3 font-medium"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {filteredTickets.map((ticket) => (
              <tr key={ticket.id} className="group hover:bg-white/[0.02] transition-colors">
                <td className="px-5 py-3"><input type="checkbox" className="rounded border-white/10 bg-white/5" /></td>
                <td className="px-5 py-3 font-mono text-slate-400">{ticket.id}</td>
                <td className="px-5 py-3 text-slate-200">{ticket.customer}</td>
                <td className="px-5 py-3 text-slate-300">{ticket.subject}</td>
                <td className="px-5 py-3">
                  <span className={cn("inline-flex rounded-full px-2 py-0.5 text-[10px] font-medium", categoryStyles[ticket.category])}>
                    {ticket.category}
                  </span>
                </td>
                <td className="px-5 py-3">
                  <span className={cn("inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-medium capitalize", statusStyles[ticket.status])}>
                    {ticket.status.replace("-", " ")}
                  </span>
                </td>
                <td className="max-w-[150px] truncate px-5 py-3 text-slate-500">
                  {ticket.resolution || "-"}
                </td>
                <td className="px-5 py-3 text-right">
                  <button className="rounded p-1 text-slate-500 hover:bg-white/5 hover:text-slate-300">
                    <MoreHorizontal size={14} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}