import { ReactNode } from "react";

interface WorkflowCardProps {
  number: string;
  icon: ReactNode;
  title: string;
  description: string;
}

export default function WorkflowCard({
  number,
  icon,
  title,
  description,
}: WorkflowCardProps) {
  return (
    <div className="relative rounded-xl border border-[#1D2942] bg-[#0D1426] p-6">

      <div className="flex items-center justify-between">
        <span className="text-[10px] font-semibold tracking-[0.15em] text-[#6B7894]">
          {number}
        </span>

        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#635BFF]/10 text-[#8B5CF6]">
          {icon}
        </div>
      </div>

      <h3 className="mt-6 text-base font-semibold">
        {title}
      </h3>

      <p className="mt-2 text-sm leading-6 text-[#A8B3CF]">
        {description}
      </p>

    </div>
  );
}