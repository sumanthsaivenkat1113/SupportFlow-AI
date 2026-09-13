import { ReactNode } from "react";

interface FeatureCardProps {
  icon: ReactNode;
  title: string;
  description: string;
  tag: string;
}

export default function FeatureCard({
  icon,
  title,
  description,
  tag,
}: FeatureCardProps) {
  return (
    <div
      className="group rounded-xl border p-6 transition duration-200 hover:-translate-y-0.5"
      style={{
        background: "rgba(13,20,38,0.72)",
        borderColor: "#1D2942",
      }}
    >
      <div className="flex items-start justify-between">

        <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-[#1D2942] bg-[#080D1C] text-[#8B5CF6] transition group-hover:border-[#635BFF]/40">
          {icon}
        </div>

        <span className="rounded-full border border-[#1D2942] px-2 py-1 text-[9px] font-medium uppercase tracking-wider text-[#6B7894]">
          {tag}
        </span>

      </div>

      <h3 className="mt-5 text-base font-semibold">
        {title}
      </h3>

      <p className="mt-2 text-sm leading-6 text-[#A8B3CF]">
        {description}
      </p>
    </div>
  );
}