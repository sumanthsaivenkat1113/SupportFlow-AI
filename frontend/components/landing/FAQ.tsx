import {
  ChevronDown,
  X,
} from "lucide-react";

import Eyebrow from "./Eyebrow";

interface FAQProps {
  openFaq: number | null;
  setOpenFaq: (value: number | null) => void;
}

const faqs = [
  {
    q: "What can I upload?",
    a: "You can create a workspace with company knowledge documents in PDF format and customer support tickets in JSON, Excel, or CSV format.",
  },
  {
    q: "Does SupportFlow automatically resolve every ticket?",
    a: "No. Tickets are first classified. Tickets that are not suitable for automation stop at the classification stage and remain available for human review.",
  },
  {
    q: "How does the AI use our company knowledge?",
    a: "Your uploaded documents are converted into searchable chunks. Relevant chunks are retrieved for each automatable ticket and used as context when generating the response.",
  },
  {
    q: "Can I export the results?",
    a: "Yes. Results can be exported in JSON, Excel, and CSV formats.",
  },
  {
    q: "Is this designed for large enterprise support teams?",
    a: "SupportFlow is positioned as a lightweight customer support automation platform for startups and lean support teams.",
  },
];

export default function FAQ({
  openFaq,
  setOpenFaq,
}: FAQProps) {
  return (
    <section
      id="faq"
      className="scroll-mt-20 border-t border-[#1D2942] bg-[#080D1C]/50"
    >
      <div className="mx-auto max-w-3xl px-5 py-24 lg:px-8">

        <div className="text-center">
          <Eyebrow>FAQ</Eyebrow>

          <h2 className="mt-4 text-3xl font-semibold tracking-[-0.03em] sm:text-4xl">
            Questions, answered.
          </h2>
        </div>

        <div className="mt-12 divide-y divide-[#1D2942] rounded-xl border border-[#1D2942] bg-[#0D1426]">

          {faqs.map((faq, index) => {
            const isOpen = openFaq === index;

            return (
              <div key={faq.q}>

                <button
                  onClick={() =>
                    setOpenFaq(isOpen ? null : index)
                  }
                  className="flex w-full items-center justify-between gap-5 px-5 py-5 text-left"
                >
                  <span className="text-sm font-medium text-white">
                    {faq.q}
                  </span>

                  {isOpen ? (
                    <X className="h-4 w-4 shrink-0 text-[#6B7894]" />
                  ) : (
                    <ChevronDown className="h-4 w-4 shrink-0 text-[#6B7894]" />
                  )}
                </button>

                {isOpen && (
                  <div className="px-5 pb-5">
                    <p className="max-w-2xl text-sm leading-6 text-[#A8B3CF]">
                      {faq.a}
                    </p>
                  </div>
                )}

              </div>
            );
          })}

        </div>
      </div>
    </section>
  );
}