import { ReactNode } from "react";

interface ValueItemProps {
  icon: ReactNode;
  title: string;
  text: string;
}

export default function ValueItem({
  icon,
  title,
  text,
}: ValueItemProps) {
  return (
    <div className="flex gap-4 px-0 py-7 sm:px-7 lg:px-10">

      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-[#1D2942] bg-[#0D1426] text-[#8B5CF6]">
        {icon}
      </div>

      <div>
        <h3 className="text-sm font-medium text-white">
          {title}
        </h3>

        <p className="mt-1 text-xs leading-5 text-[#6B7894]">
          {text}
        </p>
      </div>

    </div>
  );
}