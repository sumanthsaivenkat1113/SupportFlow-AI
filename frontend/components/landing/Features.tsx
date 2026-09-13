import {
  Bot,
  FileSpreadsheet,
  FileText,
  MessageSquare,
  Search,
  ShieldCheck,
} from "lucide-react";

import SectionHeading from "./SectionHeading";
import FeatureCard from "./FeatureCard";

const features = [
  {
    icon: FileText,
    title: "Knowledge ingestion",
    description:
      "Upload company policies, FAQs, product documentation, and internal support knowledge.",
    tag: "Knowledge",
  },
  {
    icon: Search,
    title: "Semantic retrieval",
    description:
      "Find the most relevant knowledge chunks before generating a response.",
    tag: "RAG",
  },
  {
    icon: Bot,
    title: "AI resolution",
    description:
      "Generate grounded responses using the ticket and retrieved company context.",
    tag: "Automation",
  },
  {
    icon: ShieldCheck,
    title: "Human review",
    description:
      "Tickets that should not be automated are routed for manual handling.",
    tag: "Control",
  },
  {
    icon: MessageSquare,
    title: "Ticket classification",
    description:
      "Determine whether a request can safely move through the automated resolution flow.",
    tag: "Routing",
  },
  {
    icon: FileSpreadsheet,
    title: "Flexible exports",
    description:
      "Export resolved and human-review tickets in JSON, Excel, or CSV.",
    tag: "Results",
  },
];

export default function Features() {
  return (
    <section id="features" className="scroll-mt-20">
      <div className="mx-auto max-w-7xl px-5 py-24 lg:px-8">

        <SectionHeading
          eyebrow="CORE CAPABILITIES"
          title="Everything between ticket and resolution."
          description="SupportFlow combines ticket classification, knowledge retrieval, AI resolution, and human review into one workflow."
        />

        <div className="mt-14 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => {
            const Icon = feature.icon;

            return (
              <FeatureCard
                key={feature.title}
                icon={<Icon className="h-5 w-5" />}
                title={feature.title}
                description={feature.description}
                tag={feature.tag}
              />
            );
          })}
        </div>

      </div>
    </section>
  );
}