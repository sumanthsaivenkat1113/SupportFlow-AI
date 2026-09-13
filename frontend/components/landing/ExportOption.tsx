import { ReactNode } from "react";

interface ExportOptionProps {
  icon: ReactNode;
  name: string;
  description: string;
}

export default function ExportOption({
  icon,
  name,
  description,
}: ExportOptionProps) {
  return (
    <div className="flex items-center gap-4 rounded-xl border border-[#1D2942] bg-[#0D1426] p-5 transition hover:border-[#33415F]">

      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#635BFF]/10 text-[#8B5CF6]">
        {icon}
      </div>

      <div>
        <p className="text-sm font-semibold">
          {name}
        </p>

        <p className="mt-0.5 text-xs text-[#6B7894]">
          {description}
        </p>
      </div>

    </div>
  );
}