import { Upload, Database, Tags, Search, Sparkles, Download, CheckCircle2 } from "lucide-react";
import { WorkflowStep } from "@/types/dashboard";

interface WorkflowStatusProps {
  steps: WorkflowStep[];
}

const iconMap: Record<string, React.ElementType> = {
  upload: Upload,
  database: Database,
  tag: Tags,
  search: Search,
  sparkles: Sparkles,
  download: Download,
};

export function WorkflowStatus({ steps }: WorkflowStatusProps) {
  return (
    <div className="rounded-xl border border-white/5 bg-[#131A2B] p-6">
      <h3 className="mb-6 text-sm font-semibold text-slate-200">Workflow Status</h3>
      
      <div className="relative overflow-x-auto pb-4">
        <div className="flex min-w-[800px] items-center justify-between">
          {steps.map((step, index) => {
            const Icon = iconMap[step.icon] || CheckCircle2;
            const isLast = index === steps.length - 1;
            
            return (
              <div key={step.id} className="flex flex-1 flex-col items-center text-center">
                <div className="relative mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-indigo-600/10 text-indigo-400 ring-1 ring-indigo-500/30">
                  <Icon size={20} />
                  {!isLast && (
                    <div className="absolute left-full top-1/2 h-[2px] w-full -translate-y-1/2 bg-gradient-to-r from-indigo-500/50 to-transparent" />
                  )}
                </div>
                
                <p className="text-xs font-semibold text-slate-200">{step.title}</p>
                <p className="mt-1 max-w-[100px] text-[10px] leading-tight text-slate-500">
                  {step.subtitle}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}