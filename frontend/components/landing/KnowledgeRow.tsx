import { FileText } from "lucide-react";

interface KnowledgeRowProps {
  score: string;
  title: string;
  text: string;
}

export default function KnowledgeRow({
  score,
  title,
  text,
}: KnowledgeRowProps) {
  return (
    <div className="rounded-lg border border-[#1D2942] bg-[#080D1C] p-3">

      <div className="flex items-start gap-3">

        <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-[#635BFF]/10">
          <FileText className="h-3.5 w-3.5 text-[#8B5CF6]" />
        </div>

        <div className="min-w-0 flex-1">

          <div className="flex items-center justify-between gap-3">
            <p className="truncate text-[11px] font-medium text-white">
              {title}
            </p>

            <span className="shrink-0 text-[10px] font-medium text-[#10B981]">
              {score}
            </span>
          </div>

          <p className="mt-1 truncate text-[10px] text-[#6B7894]">
            {text}
          </p>

        </div>
      </div>
    </div>
  );
}