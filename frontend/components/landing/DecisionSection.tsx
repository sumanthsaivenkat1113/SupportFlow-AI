import {
  CircleCheck,
  Users,
} from "lucide-react";

import DecisionPanel from "./DecisionPanel";

export default function DecisionSection() {
  return (
    <section className="border-y border-[#1D2942] bg-[#080D1C]/50">
      <div className="mx-auto max-w-7xl px-5 py-24 lg:px-8">

        <div className="grid gap-4 lg:grid-cols-2">

          <DecisionPanel
            type="AUTOMATED"
            icon={<CircleCheck className="h-5 w-5" />}
            color="#10B981"
            title="Let AI handle it"
            description="For tickets that can be resolved using available company knowledge, SupportFlow retrieves context and generates a response."
            items={[
              "Classified as automatable",
              "Relevant knowledge retrieved",
              "AI response generated",
              "Included in automated results",
            ]}
          />

          <DecisionPanel
            type="HUMAN REVIEW"
            icon={<Users className="h-5 w-5" />}
            color="#F59E0B"
            title="Keep a human involved"
            description="Tickets that should not be automated stop before AI resolution and remain available for human handling."
            items={[
              "Classified as non-automatable",
              "Resolution generation skipped",
              "Available for human review",
              "Included in review results",
            ]}
          />

        </div>
      </div>
    </section>
  );
}