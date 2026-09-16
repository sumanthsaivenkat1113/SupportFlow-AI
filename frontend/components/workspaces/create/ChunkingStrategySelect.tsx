// components/workspaces/create/ChunkingStrategySelect.tsx
"use client";

import React from "react";
import { ChunkingStrategy } from "@/types/workspace";

interface ChunkingStrategySelectProps {
  value: ChunkingStrategy;
  onChange: (value: ChunkingStrategy) => void;
}

const strategies: Array<{
  value: ChunkingStrategy;
  label: string;
  description: string;
}> = [
  {
    value: "Semantic",
    label: "Semantic",
    description: "Intelligent chunking based on content meaning",
  },
  {
    value: "token_based_500",
    label: "Token Based (500)",
    description: "Fixed chunks of 500 tokens",
  },
  {
    value: "Structure_aware",
    label: "Structure Aware",
    description: "Respects document structure and headings",
  },
];

export function ChunkingStrategySelect({
  value,
  onChange,
}: ChunkingStrategySelectProps) {
  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-[#F8FAFC]">
        Chunking Strategy
      </label>
      <div className="space-y-2">
        {strategies.map((strategy) => (
          <label
            key={strategy.value}
            className={`
              flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-all
              ${
                value === strategy.value
                  ? "border-[#635BFF] bg-[#635BFF]/10"
                  : "border-[#1D2942] hover:border-[#635BFF]/50"
              }
            `}
          >
            <input
              type="radio"
              name="chunkingStrategy"
              value={strategy.value}
              checked={value === strategy.value}
              onChange={(e) => onChange(e.target.value as ChunkingStrategy)}
              className="mt-1 w-4 h-4 text-[#635BFF] bg-[#080D1C] border-[#1D2942] focus:ring-[#635BFF]"
            />
            <div>
              <div className="text-[#F8FAFC] font-medium text-sm">
                {strategy.label}
              </div>
              <div className="text-[#6B7894] text-xs mt-0.5">
                {strategy.description}
              </div>
            </div>
          </label>
        ))}
      </div>
    </div>
  );
}