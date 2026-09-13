import { Check } from "lucide-react";

interface BulletProps {
  text: string;
}

export default function Bullet({ text }: BulletProps) {
  return (
    <div className="flex items-center gap-3">

      <div className="flex h-5 w-5 items-center justify-center rounded-full bg-[#10B981]/10">
        <Check className="h-3 w-3 text-[#10B981]" />
      </div>

      <span className="text-sm text-[#A8B3CF]">
        {text}
      </span>

    </div>
  );
}