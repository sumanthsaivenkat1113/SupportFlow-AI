import {
  ArrowRight,
  Sparkles,
} from "lucide-react";
import { Show, SignUpButton } from "@clerk/nextjs";
import Link from "next/link";

export default function FinalCTA() {
  return (
    <section>
      <div className="mx-auto max-w-7xl px-5 py-24 lg:px-8">
        <div
          className="relative overflow-hidden rounded-2xl border border-[#1D2942] px-6 py-16 text-center sm:px-10"
          style={{
            background:
              "radial-gradient(circle at 50% 0%, rgba(99,91,255,0.13), transparent 55%), #0D1426",
          }}
        >
          <div className="relative">
            {/* Icon */}
            <div className="mx-auto flex h-11 w-11 items-center justify-center rounded-xl bg-white/[0.06]">
              <Sparkles className="h-5 w-5 text-[#8B5CF6]" />
            </div>

            {/* Heading */}
            <h2 className="mx-auto mt-5 max-w-2xl text-3xl font-semibold tracking-[-0.03em] sm:text-4xl">
              Turn repetitive support into an automated workflow.
            </h2>

            {/* Description */}
            <p className="mx-auto mt-4 max-w-xl text-sm leading-6 text-[#A8B3CF]">
              Create a workspace, connect your knowledge, and see which
              tickets can move through AI-powered resolution.
            </p>

            {/* CTA */}
            <div className="mt-8">
              {/* Signed in: go directly to workspace creation */}
              <Show when="signed-in">
                <Link
                  href="/workspaces/create"
                  className="group mx-auto flex w-fit items-center gap-2 rounded-lg bg-white px-5 py-2.5 text-sm font-semibold text-[#050816] transition hover:bg-slate-200"
                >
                  Create your workspace

                  <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
                </Link>
              </Show>

              {/* Signed out: open sign-up modal */}
              <Show when="signed-out">
                <SignUpButton
                  mode="modal"
                  forceRedirectUrl="/workspaces/create"
                >
                  <button
                    type="button"
                    className="group mx-auto flex w-fit items-center gap-2 rounded-lg bg-white px-5 py-2.5 text-sm font-semibold text-[#050816] transition hover:bg-slate-200"
                  >
                    Create your workspace

                    <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
                  </button>
                </SignUpButton>
              </Show>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

