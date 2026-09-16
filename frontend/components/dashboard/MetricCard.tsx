import { ArrowUpRight, ArrowDownRight, Ticket, Bot, Eye, Clock } from "lucide-react";
import { MetricData } from "@/types/dashboard";
import { cn } from "@/lib/utils";

const iconMap = {
  blue: Ticket,
  purple: Bot,
  green: Eye,
  orange: Clock,
};

export function MetricCard({ title, value, change, description, variant = "blue" }: MetricData) {
  const Icon = iconMap[variant];
  const isPositive = change?.direction === "up";
  
  // For time/metrics where down is good (like resolution time), we might want different coloring
  // But following standard SaaS convention: Up=Green, Down=Red unless specified otherwise.
  // In the screenshot, Avg Resolution Time going DOWN is GREEN. 
  // Let's handle that logic here based on variant or just follow visual reference.
  
  const changeColor = 
    (title.includes("Time") && change?.direction === "down") || 
    (!title.includes("Time") && change?.direction === "up")
      ? "text-emerald-400" 
      : "text-red-400";

  const ChangeIcon = isPositive ? ArrowUpRight : ArrowDownRight;

  return (
    <div className="flex flex-col justify-between rounded-xl border border-white/5 bg-[#131A2B] p-5 transition-all hover:border-white/10">
      <div className="flex items-start justify-between">
        <div className="rounded-lg bg-white/5 p-2">
          <Icon size={20} className="text-slate-300" />
        </div>
        {change && (
          <div className={cn("flex items-center gap-1 text-xs font-medium", changeColor)}>
            <ChangeIcon size={12} />
            {change.value}
          </div>
        )}
      </div>
      
      <div className="mt-4">
        <p className="text-2xl font-bold text-white">{value}</p>
        <p className="mt-1 text-xs text-slate-500">{description}</p>
      </div>
      
      <p className="mt-3 text-[11px] font-medium uppercase tracking-wider text-slate-500">
        {title}
      </p>
    </div>
  );
}