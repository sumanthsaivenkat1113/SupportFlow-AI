import { ReactNode } from "react";

interface EyebrowProps {
  children: ReactNode;
}

export default function Eyebrow({ children }: EyebrowProps) {
  return (
    <div className="text-xs font-semibold uppercase tracking-[0.16em] text-[#8B5CF6]">
      {children}
    </div>
  );
}