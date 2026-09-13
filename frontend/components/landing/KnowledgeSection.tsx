import { Search, Sparkles } from "lucide-react";

import Eyebrow from "./Eyebrow";
import KnowledgeRow from "./KnowledgeRow";
import Bullet from "./Bullet";

const knowledge = [
  {
    score: "0.94",
    title: "Refund & cancellation policy",
    text: "Customers can request a refund within 30 days...",
  },
  {
    score: "0.89",
    title: "Billing support guidelines",
    text: "Billing disputes should be reviewed against...",
  },
  {
    score: "0.84",
    title: "Subscription FAQ",
    text: "Subscription changes take effect at the next...",
  },
  {
    score: "0.81",
    title: "Customer account policy",
    text: "Account ownership changes require verification...",
  },
];

export default function KnowledgeSection() {
  return (
    <section>
      <div className="mx-auto max-w-7xl px-5 py-24 lg:px-8">

        <div className="grid items-center gap-14 lg:grid-cols-2">

          {/* Visual */}
          <div className="relative order-2 lg:order-1">

            <div
              className="absolute -inset-8 -z-10 opacity-20 blur-3xl"
              style={{
                background:
                  "radial-gradient(circle, rgba(59,130,246,0.35), transparent 65%)",
              }}
            />

            <div className="rounded-2xl border border-[#1D2942] bg-[#0D1426] p-5">

              <div className="mb-5 flex items-center justify-between">

                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#635BFF]/10">
                    <Search className="h-4 w-4 text-[#8B5CF6]" />
                  </div>

                  <div>
                    <p className="text-xs font-semibold">
                      Knowledge retrieval
                    </p>

                    <p className="text-[10px] text-[#6B7894]">
                      Top matching chunks
                    </p>
                  </div>
                </div>

                <span className="rounded-md bg-[#10B981]/10 px-2 py-1 text-[10px] text-[#10B981]">
                  4 matches
                </span>
              </div>

              <div className="space-y-2.5">
                {knowledge.map((item) => (
                  <KnowledgeRow
                    key={item.title}
                    {...item}
                  />
                ))}
              </div>

              <div className="mt-4 rounded-lg border border-[#635BFF]/20 bg-[#635BFF]/5 p-3">
                <div className="flex items-center gap-2 text-[10px] font-medium text-[#A8B3CF]">
                  <Sparkles className="h-3.5 w-3.5 text-[#8B5CF6]" />
                  Context prepared for AI resolution
                </div>
              </div>

            </div>
          </div>

          {/* Copy */}
          <div className="order-1 lg:order-2">

            <Eyebrow>GROUNDED RESPONSES</Eyebrow>

            <h2 className="mt-4 text-3xl font-semibold tracking-[-0.03em] sm:text-4xl">
              Your knowledge.
              <br />
              <span className="text-[#8B5CF6]">
                Not AI guesswork.
              </span>
            </h2>

            <p className="mt-5 max-w-xl leading-7 text-[#A8B3CF]">
              SupportFlow retrieves relevant information from your uploaded
              knowledge base and provides that context to the AI before it
              generates a resolution.
            </p>

            <div className="mt-8 space-y-4">
              <Bullet text="Semantic chunking of company documentation" />
              <Bullet text="Vector-based knowledge retrieval" />
              <Bullet text="Top relevant context for each ticket" />
              <Bullet text="Responses grounded in your own documents" />
            </div>

          </div>

        </div>
      </div>
    </section>
  );
}