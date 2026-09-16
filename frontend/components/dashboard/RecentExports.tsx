"use client";

import { FileJson, FileSpreadsheet, FileText, Download, ExternalLink } from "lucide-react";
import { ExportFile } from "@/types/dashboard";

interface RecentExportsProps {
  exports: ExportFile[];
  onViewAll?: () => void;
  onDownload?: (file: ExportFile) => void;
}

const formatIcons = {
  json: FileJson,
  csv: FileSpreadsheet,
  xlsx: FileText,
};

const formatColors = {
  json: "text-amber-400 bg-amber-400/10",
  csv: "text-emerald-400 bg-emerald-400/10",
  xlsx: "text-blue-400 bg-blue-400/10",
};

export function RecentExports({ exports, onViewAll, onDownload }: RecentExportsProps) {
  return (
    <div className="rounded-xl border border-white/5 bg-[#131A2B] p-5">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-200">Recent Exports</h3>
        <button onClick={onViewAll} className="text-xs font-medium text-indigo-400 hover:text-indigo-300">
          View all →
        </button>
      </div>

      <div className="space-y-1">
        {exports.map((file) => {
          const Icon = formatIcons[file.format];
          const colorClass = formatColors[file.format];
          
          return (
            <div 
              key={file.id} 
              className="group flex items-center justify-between rounded-lg p-2.5 transition-colors hover:bg-white/5"
            >
              <div className="flex items-center gap-3">
                <div className={`flex h-9 w-9 items-center justify-center rounded-lg ${colorClass}`}>
                  <Icon size={16} />
                </div>
                <div>
                  <p className="truncate text-sm font-medium text-slate-200 max-w-[140px]">{file.fileName}</p>
                  <p className="text-[11px] text-slate-500">
                    {file.createdAt} • {file.ticketCount} tickets
                  </p>
                </div>
              </div>
              
              <button 
                onClick={() => onDownload?.(file)}
                className="rounded p-1.5 text-slate-500 hover:bg-white/5 hover:text-slate-300"
                aria-label="Download file"
              >
                <Download size={14} />
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}