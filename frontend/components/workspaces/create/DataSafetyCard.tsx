// components/workspaces/create/DataSafetyCard.tsx
import React from "react";
import { Shield } from "lucide-react";

export function DataSafetyCard() {
  return (
    <div className="bg-[#0D1426] rounded-xl border border-[#1D2942] p-6">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 w-10 h-10 rounded-full bg-[#635BFF] flex items-center justify-center">
          <Shield className="w-5 h-5 text-white" />
        </div>
        <div>
          <h3 className="text-[#F8FAFC] font-semibold mb-2">
            Your data is safe
          </h3>
          <p className="text-[#6B7894] text-sm leading-relaxed">
            We use secure and isolated infrastructure to protect your data. Your
            files are only used to build your workspace and are not shared with
            third parties.
          </p>
        </div>
      </div>
    </div>
  );
}