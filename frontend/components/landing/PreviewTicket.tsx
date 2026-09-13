import { MessageSquare } from "lucide-react";

interface PreviewTicketProps {
  title: string;
  type: string;
  color: "success" | "warning";
}

export default function PreviewTicket({
  title,
  type,
  color,
}: PreviewTicketProps) {
  const isSuccess = color === "success";

  return (
    <div className="flex items-center justify-between gap-4 px-4 py-3">

      <div className="flex min-w-0 items-center gap-3">
        <MessageSquare className="h-3.5 w-3.5 shrink-0 text-[#6B7894]" />

        <span className="truncate text-[10px] text-[#A8B3CF]">
          {title}
        </span>
      </div>

      <span
        className={`shrink-0 rounded-md px-2 py-1 text-[9px] ${
          isSuccess
            ? "bg-[#10B981]/10 text-[#10B981]"
            : "bg-[#F59E0B]/10 text-[#F59E0B]"
        }`}
      >
        {type}
      </span>

    </div>
  );
}