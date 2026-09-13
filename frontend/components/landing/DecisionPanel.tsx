import { Check } from "lucide-react";
import { ReactNode } from "react";

interface DecisionPanelProps {
  type: string;
  icon: ReactNode;
  color: string;
  title: string;
  description: string;
  items: string[];
}

export default function DecisionPanel({
  type,
  icon,
  color,
  title,
  description,
  items,
}: DecisionPanelProps) {
  return (
    <div className="rounded-2xl border border-[#1D2942] bg-[#0D1426] p-7 sm:p-8">

      <div className="flex items-center justify-between">

        <div
          className="flex h-10 w-10 items-center justify-center rounded-lg"
          style={{
            background: `${color}15`,
            color,
          }}
        >
          {icon}
        </div>

        <span
          className="rounded-full px-2.5 py-1 text-[9px] font-semibold tracking-wider"
          style={{
            background: `${color}12`,
            color,
          }}
        >
          {type}
        </span>

      </div>

      <h3 className="mt-7 text-xl font-semibold">
        {title}
      </h3>

      <p className="mt-3 text-sm leading-6 text-[#A8B3CF]">
        {description}
      </p>

      <div className="mt-7 space-y-3 border-t border-[#1D2942] pt-6">
        {items.map((item) => (
          <div
            key={item}
            className="flex items-center gap-3"
          >
            <Check
              className="h-3.5 w-3.5 shrink-0"
              style={{ color }}
            />

            <span className="text-xs text-[#A8B3CF]">
              {item}
            </span>
          </div>
        ))}
      </div>

    </div>
  );
}