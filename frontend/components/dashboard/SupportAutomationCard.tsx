import { Sparkles } from "lucide-react";

export function SupportAutomationCard() {
  return (
    <div className="relative overflow-hidden rounded-xl border border-indigo-500/20 bg-gradient-to-br from-indigo-950/50 to-[#131A2B] p-6">
      <div className="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-indigo-500/10 blur-3xl" />
      
      <div className="relative z-10">
        <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-500/20 text-indigo-300">
          <Sparkles size={20} />
        </div>
        
        <h3 className="text-base font-bold text-white">Smart Support. Faster Resolutions.</h3>
        <p className="mt-2 text-xs leading-relaxed text-slate-400">
          SupportFlow AI uses RAG and advanced AI to deliver accurate, grounded responses and automate your support workflow.
        </p>
      </div>
    </div>
  );
}