import {
  Bot,
  Database,
  FileText,
  Search,
} from "lucide-react";

import SectionHeading from "./SectionHeading";
import WorkflowCard from "./WorkflowCard";

const workflow = [
  {
    number: "01",
    icon: FileText,
    title: "Upload",
    description:
      "Create a workspace and upload your company knowledge and customer tickets.",
  },
  {
    number: "02",
    icon: Search,
    title: "Classify",
    description:
      "Analyze each ticket and determine whether it is suitable for automation.",
  },
  {
    number: "03",
    icon: Database,
    title: "Retrieve",
    description:
      "Search your knowledge base for the most relevant context.",
  },
  {
    number: "04",
    icon: Bot,
    title: "Resolve",
    description:
      "Generate a grounded response or route the ticket to human review.",
  },
];

export default function Workflow() {
  return (
    <section
      id="workflow"
      className="scroll-mt-20 border-y border-[#1D2942] bg-[#080D1C]/50"
    >
      <div className="mx-auto max-w-7xl px-5 py-24 lg:px-8">

        <SectionHeading
          eyebrow="HOW IT WORKS"
          title="A simple path from knowledge to resolution."
          description="Your support workflow stays predictable. AI handles the repetitive steps while your team handles the exceptions."
        />

        <div className="mt-14 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {workflow.map((item) => {
            const Icon = item.icon;

            return (
              <WorkflowCard
                key={item.number}
                number={item.number}
                icon={<Icon className="h-5 w-5" />}
                title={item.title}
                description={item.description}
              />
            );
          })}
        </div>

      </div>
    </section>
  );
}