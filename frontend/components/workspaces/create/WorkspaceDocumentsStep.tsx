// components/workspaces/create/WorkspaceDocumentsStep.tsx
"use client";

import React from "react";
import { PdfUploadZone } from "./PdfUploadZone";
import { ChunkingStrategySelect } from "./ChunkingStrategySelect";
import { ChunkingStrategy } from "@/types/workspace";

interface WorkspaceDocumentsStepProps {
  workspaceName: string;
  onWorkspaceNameChange: (value: string) => void;
  pdfFiles: File[];
  onPdfFilesChange: (files: File[]) => void;
  chunkingStrategy: ChunkingStrategy;
  onChunkingStrategyChange: (value: ChunkingStrategy) => void;
  error?: string;
}

export function WorkspaceDocumentsStep({
  workspaceName,
  onWorkspaceNameChange,
  pdfFiles,
  onPdfFilesChange,
  chunkingStrategy,
  onChunkingStrategyChange,
  error,
}: WorkspaceDocumentsStepProps) {
  const charCount = workspaceName.length;
  const maxChars = 50;

  return (
    <div className="bg-[#0D1426] rounded-xl border border-[#1D2942] p-6">
      <div className="mb-6">
        <h2 className="text-[#F8FAFC] text-xl font-semibold mb-2">
          Workspace & Documents
        </h2>
        <p className="text-[#6B7894] text-sm">
          Give your workspace a name and upload up to 5 PDF files containing your
          company policies, FAQs, guidelines, etc.
        </p>
      </div>

      <div className="space-y-6">
        {/* Workspace Name */}
        <div>
          <label
            htmlFor="workspaceName"
            className="block text-[#F8FAFC] font-medium mb-2"
          >
            Workspace Name *
          </label>
          <div className="relative">
            <input
              type="text"
              id="workspaceName"
              value={workspaceName}
              onChange={(e) => onWorkspaceNameChange(e.target.value)}
              placeholder="e.g. Acme Corp Support"
              maxLength={maxChars}
              className={`
                w-full px-4 py-3 bg-[#080D1C] border rounded-lg text-[#F8FAFC] placeholder-[#6B7894]
                focus:outline-none focus:ring-2 focus:ring-[#635BFF] transition-all
                ${
                  error
                    ? "border-[#F43F5E]"
                    : "border-[#1D2942] hover:border-[#635BFF]/50"
                }
              `}
              aria-required="true"
              aria-invalid={!!error}
              aria-describedby="workspaceName-error"
            />
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-[#6B7894] text-sm">
              {charCount}/{maxChars}
            </div>
          </div>
          {error && (
            <p id="workspaceName-error" className="text-[#F43F5E] text-sm mt-1">
              {error}
            </p>
          )}
        </div>

        {/* PDF Upload */}
        <div>
          <label className="block text-[#F8FAFC] font-medium mb-3">
            Upload PDF Documents (up to 5) *
          </label>
          <PdfUploadZone
            files={pdfFiles}
            maxFiles={5}
            maxSizeMB={10}
            onFilesChange={onPdfFilesChange}
          />
        </div>

        {/* Advanced Options */}
        <div className="pt-4 border-t border-[#1D2942]">
          <details className="group">
            <summary className="flex items-center gap-2 cursor-pointer text-[#A8B3CF] hover:text-[#F8FAFC] transition-colors">
              <span className="text-sm font-medium">Advanced Options</span>
              <svg
                className="w-4 h-4 transition-transform group-open:rotate-180"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </summary>
            <div className="mt-4">
              <ChunkingStrategySelect
                value={chunkingStrategy}
                onChange={onChunkingStrategyChange}
              />
            </div>
          </details>
        </div>
      </div>
    </div>
  );
}