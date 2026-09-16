// components/workspaces/create/TicketUploadZone.tsx
"use client";

import React, { useCallback, useState, useRef } from "react";
import { CloudUpload, FileText, X } from "lucide-react";

interface TicketUploadZoneProps {
  file: File | null;
  onFileChange: (file: File | null) => void;
  error?: string;
}

const ACCEPTED_FORMATS = [".xlsx", ".xls", ".csv", ".json"];
const ACCEPTED_TYPES = [
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "application/vnd.ms-excel",
  "text/csv",
  "application/json",
];

export function TicketUploadZone({
  file,
  onFileChange,
  error,
}: TicketUploadZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [localError, setLocalError] = useState<string | undefined>(error);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = useCallback((file: File): string | null => {
    // Check file extension
    const extension = "." + file.name.split(".").pop()?.toLowerCase();
    if (!ACCEPTED_FORMATS.includes(extension)) {
      return "Only Excel, CSV, and JSON files are supported.";
    }

    // Check MIME type (if available)
    if (file.type && !ACCEPTED_TYPES.includes(file.type)) {
      if (!ACCEPTED_FORMATS.includes(extension)) {
        return "Invalid file format.";
      }
    }

    return null;
  }, []);

  const handleFile = useCallback(
    (newFile: File) => {
      setLocalError(undefined);
      
      const validationError = validateFile(newFile);
      if (validationError) {
        setLocalError(validationError);
        return;
      }

      onFileChange(newFile);
      
      // Clear the input value to allow selecting the same file again if removed and re-added
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    },
    [onFileChange, validateFile]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);

      const droppedFiles = Array.from(e.dataTransfer.files);
      if (droppedFiles.length > 0) {
        handleFile(droppedFiles[0]);
      }
    },
    [handleFile]
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const selectedFiles = e.target.files;
      if (selectedFiles && selectedFiles.length > 0) {
        handleFile(selectedFiles[0]);
      }
    },
    [handleFile]
  );

  // NEW: Handle click on the entire zone to trigger file input
  const handleZoneClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const removeFile = useCallback((e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering the zone click when clicking remove
    onFileChange(null);
    setLocalError(undefined);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }, [onFileChange]);

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
  };

  const getFileIcon = (fileName: string) => {
    const extension = fileName.split(".").pop()?.toLowerCase();
    const colors: Record<string, string> = {
      xlsx: "text-[#10B981]",
      xls: "text-[#10B981]",
      csv: "text-[#3B82F6]",
      json: "text-[#F59E0B]",
    };
    return colors[extension || ""] || "text-[#635BFF]";
  };

  return (
    <div className="space-y-4">
      <div
        className={`
          border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 cursor-pointer
          ${
            isDragOver
              ? "border-[#635BFF] bg-[#635BFF]/10"
              : "border-[#1D2942] hover:border-[#635BFF]/50"
          }
        `}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleZoneClick}
        role="button"
        tabIndex={0}
        aria-label="Upload tickets file"
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            handleZoneClick();
          }
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPTED_FORMATS.join(",")}
          onChange={handleFileInput}
          className="hidden"
          aria-hidden="true"
        />

        {!file ? (
          // pointer-events-none ensures clicks pass through to the parent div
          <div className="flex flex-col items-center gap-3 pointer-events-none">
            <div
              className={`
                w-16 h-16 rounded-full flex items-center justify-center
                ${isDragOver ? "bg-[#635BFF]" : "bg-[#1D2942]"}
              `}
            >
              <CloudUpload
                className={`w-8 h-8 ${
                  isDragOver ? "text-white" : "text-[#635BFF]"
                }`}
              />
            </div>

            <div>
              <p className="text-[#F8FAFC] font-medium">
                Upload tickets file
              </p>
              <p className="text-[#6B7894] text-sm mt-1">
                Excel, CSV or JSON (Max 20 records)
              </p>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-4 pointer-events-none">
            <div className="flex items-center gap-3 flex-1">
              <FileText className={`w-8 h-8 ${getFileIcon(file.name)}`} />
              <div className="flex-1 min-w-0 text-left">
                <p className="text-[#F8FAFC] font-medium truncate">
                  {file.name}
                </p>
                <p className="text-[#6B7894] text-sm">
                  {formatFileSize(file.size)}
                </p>
              </div>
            </div>
            {/* pointer-events-auto allows the remove button to be clicked independently */}
            <button
              type="button"
              onClick={removeFile}
              className="pointer-events-auto p-2 hover:bg-[#1D2942] rounded-lg transition-colors"
              aria-label={`Remove ${file.name}`}
            >
              <X className="w-5 h-5 text-[#6B7894] hover:text-[#F43F5E]" />
            </button>
          </div>
        )}
      </div>

      {(localError || error) && (
        <div className="text-[#F43F5E] text-sm" role="alert">
          {localError || error}
        </div>
      )}

      {/* Accepted formats info */}
      <div className="bg-[#0D1426] rounded-xl border border-[#1D2942] p-4">
        <h4 className="text-[#F8FAFC] font-medium mb-3 text-sm">
          Accepted formats
        </h4>
        <div className="flex flex-wrap gap-3">
          <div className="flex items-center gap-2 px-3 py-2 bg-[#080D1C] rounded-lg">
            <div className="w-8 h-8 bg-[#10B981]/20 rounded flex items-center justify-center">
              <span className="text-[#10B981] text-xs font-bold">XLSX</span>
            </div>
            <span className="text-[#A8B3CF] text-sm">.xlsx</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-2 bg-[#080D1C] rounded-lg">
            <div className="w-8 h-8 bg-[#10B981]/20 rounded flex items-center justify-center">
              <span className="text-[#10B981] text-xs font-bold">XLS</span>
            </div>
            <span className="text-[#A8B3CF] text-sm">.xls</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-2 bg-[#080D1C] rounded-lg">
            <div className="w-8 h-8 bg-[#3B82F6]/20 rounded flex items-center justify-center">
              <span className="text-[#3B82F6] text-xs font-bold">CSV</span>
            </div>
            <span className="text-[#A8B3CF] text-sm">.csv</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-2 bg-[#080D1C] rounded-lg">
            <div className="w-8 h-8 bg-[#F59E0B]/20 rounded flex items-center justify-center">
              <span className="text-[#F59E0B] text-xs font-bold">JSON</span>
            </div>
            <span className="text-[#A8B3CF] text-sm">.json</span>
          </div>
        </div>
      </div>
    </div>
  );
}