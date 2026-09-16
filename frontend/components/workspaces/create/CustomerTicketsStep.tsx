// components/workspaces/create/CustomerTicketsStep.tsx
"use client";

import React from "react";
import { TicketUploadZone } from "./TicketUploadZone";

interface CustomerTicketsStepProps {
  ticketFile: File | null;
  onTicketFileChange: (file: File | null) => void;
  error?: string;
}

export function CustomerTicketsStep({
  ticketFile,
  onTicketFileChange,
  error,
}: CustomerTicketsStepProps) {
  return (
    <div className="bg-[#0D1426] rounded-xl border border-[#1D2942] p-6">
      <div className="mb-6">
        <h2 className="text-[#F8FAFC] text-xl font-semibold mb-2">
          Customer Tickets
        </h2>
        <p className="text-[#6B7894] text-sm">
          Upload customer support tickets (up to 20) via Excel, CSV or JSON file.
        </p>
      </div>

      <TicketUploadZone
        file={ticketFile}
        onFileChange={onTicketFileChange}
        error={error}
      />
    </div>
  );
}