import {
  FileJson,
  FileSpreadsheet,
  FileText,
} from "lucide-react";

import Eyebrow from "./Eyebrow";
import ExportOption from "./ExportOption";

export default function ExportSection() {
  return (
    <section>
      <div className="mx-auto max-w-7xl px-5 py-24 lg:px-8">

        <div className="mx-auto max-w-3xl text-center">

          <Eyebrow>RESULTS & EXPORTS</Eyebrow>

          <h2 className="mt-4 text-3xl font-semibold tracking-[-0.03em] sm:text-4xl">
            Your results, your format.
          </h2>

          <p className="mx-auto mt-5 max-w-xl leading-7 text-[#A8B3CF]">
            Once processing is complete, export your ticket results and
            continue working with the data wherever your team needs it.
          </p>

        </div>

        <div className="mx-auto mt-12 grid max-w-4xl gap-3 sm:grid-cols-3">

          <ExportOption
            icon={<FileJson className="h-5 w-5" />}
            name="JSON"
            description="Structured data"
          />

          <ExportOption
            icon={<FileSpreadsheet className="h-5 w-5" />}
            name="Excel"
            description="Spreadsheet-ready"
          />

          <ExportOption
            icon={<FileText className="h-5 w-5" />}
            name="CSV"
            description="Simple & portable"
          />

        </div>
      </div>
    </section>
  );
}