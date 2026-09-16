// components/workspaces/create/WorkspaceNextSteps.tsx
import React from "react";
import { FileText, Brain, Download } from "lucide-react";

export function WorkspaceNextSteps() {
  const steps = [
    {
      icon: FileText,
      title: "PDF Processing",
      description:
        "We'll convert your PDFs to text, create chunks using semantic chunking, and store them in a vector database.",
    },
    {
      icon: Brain,
      title: "AI Classification",
      description:
        "Our AI will classify tickets, search relevant knowledge, and generate grounded responses.",
    },
    {
      icon: Download,
      title: "Export Results",
      description:
        "You can then export the resolved tickets in JSON, Excel or CSV format.",
    },
  ];

  return (
    <div className="bg-[#0D1426] rounded-xl border border-[#1D2942] p-6">
      <h3 className="text-[#F8FAFC] font-semibold text-lg mb-4">
        What happens next?
      </h3>
      <div className="space-y-4">
        {steps.map((step, index) => (
          <div key={index} className="flex gap-3">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#635BFF] flex items-center justify-center text-white font-semibold text-sm">
              {index + 1}
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <step.icon className="w-4 h-4 text-[#635BFF]" />
                <h4 className="text-[#F8FAFC] font-medium text-sm">
                  {step.title}
                </h4>
              </div>
              <p className="text-[#6B7894] text-sm leading-relaxed">
                {step.description}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}