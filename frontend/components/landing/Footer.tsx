import { Sparkles } from "lucide-react";

interface FooterProps {
  scrollTo: (id: string) => void;
}

export default function Footer({ scrollTo }: FooterProps) {
  return (
    <footer className="border-t border-[#1D2942]">
      <div className="mx-auto flex max-w-7xl flex-col gap-5 px-5 py-8 sm:flex-row sm:items-center sm:justify-between lg:px-8">

        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-md bg-[#635BFF]">
            <Sparkles className="h-3.5 w-3.5 text-white" />
          </div>

          <span className="text-sm font-semibold">
            SupportFlow{" "}
            <span className="text-[#8B5CF6]">AI</span>
          </span>
        </div>

        <p className="text-xs text-[#6B7894]">
          AI-powered customer support automation.
        </p>

        <div className="flex items-center gap-5">
          <button
            onClick={() => scrollTo("features")}
            className="text-xs text-[#6B7894] hover:text-white"
          >
            Features
          </button>

          <button
            onClick={() => scrollTo("faq")}
            className="text-xs text-[#6B7894] hover:text-white"
          >
            FAQ
          </button>

          <a
            href="/sign-in"
            className="text-xs text-[#6B7894] hover:text-white"
          >
            Sign in
          </a>
        </div>

      </div>
    </footer>
  );
}