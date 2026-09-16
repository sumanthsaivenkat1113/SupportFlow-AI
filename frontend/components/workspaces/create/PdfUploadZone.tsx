// components/workspaces/create/PdfUploadZone.tsx
"use client";

import React, { useCallback, useState, useRef } from "react";
import { CloudUpload, FileText, Trash2, X } from "lucide-react";

interface PdfUploadZoneProps {
  files: File[];
  maxFiles?: number;
  maxSizeMB?: number;
  onFilesChange: (files: File[]) => void;
  error?: string;
}

export function PdfUploadZone({
  files,
  maxFiles = 5,
  maxSizeMB = 10,
  onFilesChange,
  error,
}: PdfUploadZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [localError, setLocalError] = useState<string | undefined>(error);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = useCallback(
    (file: File): string | null => {
      // Check file type
      if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
        return "Only PDF files are supported.";
      }

      // Check file size
      if (file.size > maxSizeMB * 1024 * 1024) {
        return `Each file must be ${maxSizeMB}MB or smaller.`;
      }

      // Check for duplicates
      const isDuplicate = files.some(
        (existingFile) =>
          existingFile.name === file.name &&
          existingFile.size === file.size
      );
      if (isDuplicate) {
        return "This file has already been added.";
      }

      return null;
    },
    [files, maxSizeMB]
  );

  const handleFiles = useCallback(
    (newFiles: File[]) => {
      setLocalError(undefined);

      if (files.length + newFiles.length > maxFiles) {
        setLocalError(`You can upload a maximum of ${maxFiles} PDF files.`);
        return;
      }

      const validFiles: File[] = [];
      let hasError = false;

      newFiles.forEach((file) => {
        const validationError = validateFile(file);
        if (validationError) {
          setLocalError(validationError);
          hasError = true;
        } else {
          validFiles.push(file);
        }
      });

      if (!hasError && validFiles.length > 0) {
        onFilesChange([...files, ...validFiles]);
      }
      
      // Clear the input value to allow selecting the same file again
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    },
    [files, maxFiles, onFilesChange, validateFile]
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
        handleFiles(droppedFiles);
      }
    },
    [handleFiles]
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const selectedFiles = Array.from(e.target.files || []);
      if (selectedFiles.length > 0) {
        handleFiles(selectedFiles);
      }
    },
    [handleFiles]
  );

  const handleZoneClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const removeFile = useCallback(
    (index: number) => {
      const newFiles = files.filter((_, i) => i !== index);
      onFilesChange(newFiles);
      setLocalError(undefined);
    },
    [files, onFilesChange]
  );

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
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
        aria-label="Upload PDF files"
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
          accept=".pdf,application/pdf"
          multiple
          onChange={handleFileInput}
          className="hidden"
          aria-hidden="true"
        />
        
        <div className="flex flex-col items-center gap-3 pointer-events-none">
          <div
            className={`
              w-16 h-16 rounded-full flex items-center justify-center
              ${isDragOver ? "bg-[#635BFF]" : "bg-[#1D2942]"}
            `}
          >
            <CloudUpload
              className={`w-8 h-8 ${isDragOver ? "text-white" : "text-[#635BFF]"}`}
            />
          </div>
          
          <div>
            <p className="text-[#F8FAFC] font-medium">
              Drag and drop PDF files here, or click to browse
            </p>
            <p className="text-[#6B7894] text-sm mt-1">
              Supports PDF only • Max {maxFiles} files • Up to {maxSizeMB}MB each
            </p>
          </div>
        </div>
      </div>

      {(localError || error) && (
        <div className="text-[#F43F5E] text-sm" role="alert">
          {localError || error}
        </div>
      )}

      {files.length > 0 && (
        <div className="bg-[#0D1426] rounded-xl border border-[#1D2942] p-4">
          <h4 className="text-[#F8FAFC] font-medium mb-3">
            Uploaded Files ({files.length}/{maxFiles})
          </h4>
          <div className="space-y-2">
            {files.map((file, index) => (
              <div
                key={`${file.name}-${index}`}
                className="flex items-center justify-between p-3 bg-[#080D1C] rounded-lg"
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <div className="w-10 h-10 bg-[#635BFF]/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <FileText className="w-5 h-5 text-[#635BFF]" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-[#F8FAFC] text-sm truncate">
                      {file.name}
                    </p>
                    <p className="text-[#6B7894] text-xs">
                      {formatFileSize(file.size)}
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(index);
                  }}
                  className="p-2 hover:bg-[#1D2942] rounded-lg transition-colors ml-2"
                  aria-label={`Remove ${file.name}`}
                >
                  <X className="w-4 h-4 text-[#6B7894] hover:text-[#F43F5E]" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}