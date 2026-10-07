import { ArrowRight } from "lucide-react";
import ProductPreview from "./ProductPreview";
import { Show, SignUpButton } from "@clerk/nextjs";
import Link from "next/link";

interface HeroProps {
  scrollTo: (id: string) => void;
}

export default function Hero({ scrollTo }: HeroProps) {
  return (
    <section id="top" className="relative">
      <div className="mx-auto max-w-7xl px-5 pb-20 pt-20 lg:px-8 lg:pb-28 lg:pt-28">

        <div className="mx-auto max-w-4xl text-center">

          {/* Badge */}
          <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-[#1D2942] bg-[#0D1426]/70 px-3.5 py-1.5 text-xs font-medium text-slate-300">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#10B981] opacity-60" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-[#10B981]" />
            </span>

            AI-powered customer support automation
          </div>

          {/* Heading */}
          <h1 className="text-4xl font-semibold leading-[1.08] tracking-[-0.04em] text-white sm:text-5xl lg:text-7xl">
            Resolve support tickets
            <br />

            <span
              style={{
                background:
                  "linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              with AI that understands.
            </span>
          </h1>

          <p className="mx-auto mt-7 max-w-2xl text-base leading-7 text-[#A8B3CF] sm:text-lg">
            Connect your company knowledge, upload customer tickets, and let
            SupportFlow classify, retrieve, resolve, and route every request
            automatically.
          </p>

          {/* CTA */}
          <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
            {/* Signed in: go directly to workspace creation */}
            <Show when="signed-in">
              <Link
                href="/workspaces/create"
                className="group flex h-11 items-center justify-center gap-2 rounded-lg bg-white px-6 text-sm font-semibold text-[#050816] transition hover:bg-slate-200"
              >
                Create workspace
                <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
              </Link>
            </Show>

            {/* Signed out: open sign-up modal, then redirect to workspace creation */}
            <Show when="signed-out">
              <SignUpButton mode="modal" forceRedirectUrl="/workspaces/create">
                <button
                  type="button"
                  className="group flex h-11 items-center justify-center gap-2 rounded-lg bg-white px-6 text-sm font-semibold text-[#050816] transition hover:bg-slate-200"
                >
                  Create workspace
                  <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
                </button>
              </SignUpButton>
            </Show>

            {/* See how it works */}
            <button
              type="button"
              onClick={() => scrollTo("workflow")}
              className="flex h-11 items-center justify-center gap-2 rounded-lg border border-[#1D2942] bg-[#0D1426]/70 px-6 text-sm font-medium text-slate-200 transition hover:border-[#33415F] hover:bg-[#111A30]"
            >
              See how it works
            </button>
          </div>



          <p className="mt-5 text-xs text-[#6B7894]">
            Built for startups and lean support teams.
          </p>
        </div>

        <ProductPreview />
      </div>
    </section>
  );
}