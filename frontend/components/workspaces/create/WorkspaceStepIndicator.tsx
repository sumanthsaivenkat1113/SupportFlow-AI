// components/workspaces/create/WorkspaceStepIndicator.tsx
import React from "react";

interface StepIndicatorProps {
  currentStep: number;
  steps: Array<{
    number: number;
    label: string;
  }>;
}

export function WorkspaceStepIndicator({
  currentStep,
  steps,
}: StepIndicatorProps) {
  return (
    <div className="flex items-center gap-4 mb-8">
      {steps.map((step, index) => {
        const isCompleted = currentStep > step.number;
        const isActive = currentStep === step.number;
        
        return (
          <React.Fragment key={step.number}>
            <div className="flex items-center gap-3">
              <div
                className={`
                  w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold
                  transition-colors duration-200
                  ${
                    isCompleted
                      ? "bg-[#10B981] text-white"
                      : isActive
                      ? "bg-[#635BFF] text-white"
                      : "bg-[#1D2942] text-[#6B7894]"
                  }
                `}
              >
                {isCompleted ? (
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                ) : (
                  step.number
                )}
              </div>
              <span
                className={`
                  text-sm font-medium
                  ${
                    isActive
                      ? "text-[#F8FAFC]"
                      : isCompleted
                      ? "text-[#10B981]"
                      : "text-[#6B7894]"
                  }
                `}
              >
                {step.label}
              </span>
            </div>
            {index < steps.length - 1 && (
              <div
                className={`
                  flex-1 h-px max-w-[120px]
                  ${
                    isCompleted
                      ? "bg-[#10B981]"
                      : "bg-[#1D2942]"
                  }
                `}
              />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}