import {
  Database,
  Inbox,
  MessageSquare,
  Sparkles,
} from "lucide-react";

import PreviewTicket from "./PreviewTicket";

export default function ProductPreview() {
  const sidebarItems = [
    ["Overview", Inbox],
    ["Tickets", MessageSquare],
    ["Knowledge", Database],
  ];

  const stats = [
    ["Tickets", "248"],
    ["Automated", "184"],
    ["Human review", "64"],
    ["Knowledge", "32"],
  ];

  return (
    <div className="relative mx-auto mt-16 max-w-6xl">

      <div
        className="absolute -inset-10 -z-10 opacity-30 blur-3xl"
        style={{
          background:
            "radial-gradient(circle, rgba(99,91,255,0.35), transparent 65%)",
        }}
      />

      <div className="overflow-hidden rounded-2xl border border-[#1D2942] bg-[#0D1426] shadow-2xl shadow-black/40">

        {/* Browser Bar */}
        <div className="flex h-11 items-center border-b border-[#1D2942] bg-[#080D1C] px-4">
          <div className="flex gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-[#F43F5E]/70" />
            <span className="h-2.5 w-2.5 rounded-full bg-[#F59E0B]/70" />
            <span className="h-2.5 w-2.5 rounded-full bg-[#10B981]/70" />
          </div>

          <div className="mx-auto hidden rounded-md border border-[#1D2942] bg-[#0D1426] px-20 py-1 text-[10px] text-[#6B7894] sm:block">
            app.supportflow.ai / workspace
          </div>
        </div>

        <div className="grid min-h-[390px] md:grid-cols-[190px_1fr]">

          {/* Sidebar */}
          <aside className="hidden border-r border-[#1D2942] bg-[#080D1C] p-4 md:block">
            <div className="mb-6 flex items-center gap-2">
              <div className="flex h-6 w-6 items-center justify-center rounded-md bg-[#635BFF]">
                <Sparkles className="h-3 w-3 text-white" />
              </div>

              <span className="text-xs font-semibold">
                SupportFlow
              </span>
            </div>

            <div className="space-y-1">
              {sidebarItems.map(([label, Icon], index) => {
                const IconComponent = Icon as any;

                return (
                  <div
                    key={label as string}
                    className={`flex items-center gap-2.5 rounded-md px-2.5 py-2 text-[11px] ${
                      index === 0
                        ? "bg-[#635BFF]/10 text-white"
                        : "text-[#6B7894]"
                    }`}
                  >
                    <IconComponent className="h-3.5 w-3.5" />
                    {label as string}
                  </div>
                );
              })}
            </div>
          </aside>

          {/* Dashboard */}
          <div className="p-5 sm:p-7">

            <div className="mb-6 flex items-center justify-between">
              <div>
                <p className="text-[10px] uppercase tracking-[0.14em] text-[#6B7894]">
                  Workspace
                </p>

                <h3 className="mt-1 text-lg font-semibold">
                  Acme Support
                </h3>
              </div>

              <div className="hidden items-center gap-2 rounded-md border border-[#1D2942] px-3 py-1.5 text-[10px] text-[#A8B3CF] sm:flex">
                <span className="h-1.5 w-1.5 rounded-full bg-[#10B981]" />
                Processing
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {stats.map(([label, value]) => (
                <div
                  key={label}
                  className="rounded-lg border border-[#1D2942] bg-[#080D1C] p-3"
                >
                  <p className="text-[10px] text-[#6B7894]">
                    {label}
                  </p>

                  <p className="mt-1 text-lg font-semibold">
                    {value}
                  </p>
                </div>
              ))}
            </div>

            {/* Ticket Processing */}
            <div className="mt-4 rounded-xl border border-[#1D2942] bg-[#080D1C]">

              <div className="flex items-center justify-between border-b border-[#1D2942] px-4 py-3">
                <span className="text-xs font-medium">
                  Ticket processing
                </span>

                <span className="text-[10px] text-[#6B7894]">
                  Live pipeline
                </span>
              </div>

              <div className="divide-y divide-[#1D2942]">
                <PreviewTicket
                  title="How can I update my billing address?"
                  type="Automated"
                  color="success"
                />

                <PreviewTicket
                  title="My account has been charged twice"
                  type="Human review"
                  color="warning"
                />

                <PreviewTicket
                  title="Where can I download my invoice?"
                  type="Automated"
                  color="success"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}