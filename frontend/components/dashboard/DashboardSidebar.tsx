"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, FolderKanban, Settings, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils"

const navigationItems = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Workspaces", href: "/workspaces/create", icon: FolderKanban },
  { label: "Knowledge Base", href: "/knowledge-base", icon: Sparkles },
  { label: "Settings", href: "/settings", icon: Settings },
];

export function DashboardSidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 hidden h-screen w-64 flex-col border-r border-white/5 bg-[#0B0F19] lg:flex">
      <div className="flex h-16 items-center gap-2 px-6">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-white">
          <Sparkles size={18} />
        </div>
        <span className="text-lg font-bold tracking-tight text-white">
          SupportFlow <span className="font-normal text-indigo-400">AI</span>
        </span>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigationItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-indigo-600/10 text-indigo-400"
                  : "text-slate-400 hover:bg-white/5 hover:text-slate-100"
              )}
            >
              <item.icon
                size={18}
                className={cn(isActive ? "text-indigo-400" : "text-slate-500 group-hover:text-slate-300")}
              />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-white/5 p-4">
        <div className="rounded-xl bg-gradient-to-br from-indigo-900/40 to-purple-900/40 p-4">
          <p className="mb-2 text-xs font-semibold text-indigo-300">Automate your support</p>
          <p className="mb-3 text-[11px] leading-relaxed text-slate-400">
            Upload docs and let SupportFlow AI handle the rest.
          </p>
          <button className="w-full rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-indigo-500">
            + Create Workspace
          </button>
        </div>
      </div>
    </aside>
  );
}