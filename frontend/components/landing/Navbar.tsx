"use client";

import {
  ArrowRight,
  Menu,
  Sparkles,
  X,
} from "lucide-react";
import {
  Show,
  SignInButton,
  SignUpButton,
  UserButton,
} from "@clerk/nextjs";

interface NavbarProps {
  mobileOpen: boolean;
  setMobileOpen: (value: boolean) => void;
  scrollTo: (id: string) => void;
}

export default function Navbar({
  mobileOpen,
  setMobileOpen,
  scrollTo,
}: NavbarProps) {
  const navigation = [
    ["Features", "features"],
    ["How it works", "workflow"],
    ["FAQ", "faq"],
  ];

  const closeMobileMenu = () => {
    setMobileOpen(false);
  };

  return (
    <header className="sticky top-0 z-50 border-b border-white/[0.06] bg-[#050816]/85 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-5 lg:px-8">

        {/* Logo */}
        <button
          onClick={() => scrollTo("top")}
          className="flex items-center gap-2.5"
        >
          <div
            className="flex h-8 w-8 items-center justify-center rounded-lg"
            style={{
              background:
                "linear-gradient(135deg, #635BFF 0%, #8B5CF6 50%, #3B82F6 100%)",
            }}
          >
            <Sparkles className="h-4 w-4 text-white" />
          </div>

          <span className="text-[15px] font-semibold tracking-tight text-white">
            SupportFlow
            <span className="text-[#8B5CF6]"> AI</span>
          </span>
        </button>

        {/* Desktop Navigation */}
        <nav className="hidden items-center gap-8 md:flex">
          {navigation.map(([label, id]) => (
            <button
              key={id}
              onClick={() => scrollTo(id)}
              className="text-sm text-slate-400 transition hover:text-white"
            >
              {label}
            </button>
          ))}
        </nav>

        {/* Desktop Actions */}
        <div className="hidden items-center gap-3 md:flex">

          {/* Signed Out */}
          <Show when="signed-out">
            <SignInButton mode="modal" forceRedirectUrl="/workspace/new">
              <button className="px-3 py-2 text-sm font-medium text-slate-300 transition hover:text-white">
                Sign in
              </button>
            </SignInButton>

            <SignUpButton mode="modal" forceRedirectUrl="/workspace/new">
              <button className="group flex items-center gap-2 rounded-lg bg-white px-4 py-2 text-sm font-semibold text-[#050816] transition hover:bg-slate-200">
                Get started

                <ArrowRight className="h-3.5 w-3.5 transition group-hover:translate-x-0.5" />
              </button>
            </SignUpButton>
          </Show>

          {/* Signed In */}
          <Show when="signed-in">
            <div className="flex items-center gap-3">
              

              <UserButton
                appearance={{
                  elements: {
                    avatarBox: "h-9 w-9",
                  },
                }}
              />
            </div>
          </Show>
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="rounded-lg border border-[#1D2942] p-2 text-slate-300 md:hidden"
          aria-label="Toggle menu"
        >
          {mobileOpen ? (
            <X className="h-5 w-5" />
          ) : (
            <Menu className="h-5 w-5" />
          )}
        </button>
      </div>

      {/* Mobile Menu */}
      {mobileOpen && (
        <div className="border-t border-[#1D2942] bg-[#080D1C] px-5 py-5 md:hidden">
          <div className="flex flex-col gap-1">

            {/* Navigation */}
            {navigation.map(([label, id]) => (
              <button
                key={id}
                onClick={() => {
                  scrollTo(id);
                  closeMobileMenu();
                }}
                className="rounded-lg px-3 py-3 text-left text-sm text-slate-300 hover:bg-white/[0.04] hover:text-white"
              >
                {label}
              </button>
            ))}

            <div className="my-3 h-px bg-[#1D2942]" />

            {/* Signed Out Mobile */}
            <Show when="signed-out">
              <SignInButton mode="modal" forceRedirectUrl="/home">
                <button
                  onClick={closeMobileMenu}
                  className="rounded-lg px-3 py-3 text-left text-sm text-slate-300 transition hover:bg-white/[0.04] hover:text-white"
                >
                  Sign in
                </button>
              </SignInButton>

              <SignUpButton mode="modal" forceRedirectUrl="/workspace/new">
                <button
                  onClick={closeMobileMenu}
                  className="mt-1 flex items-center justify-center gap-2 rounded-lg bg-white px-4 py-3 text-sm font-semibold text-[#050816] transition hover:bg-slate-200"
                >
                  Get started

                  <ArrowRight className="h-3.5 w-3.5" />
                </button>
              </SignUpButton>
            </Show>

            {/* Signed In Mobile */}
            <Show when="signed-in">
              <a
                href="/home"
                onClick={closeMobileMenu}
                className="rounded-lg px-3 py-3 text-sm text-slate-300 transition hover:bg-white/[0.04] hover:text-white"
              >
                Dashboard
              </a>

              <div className="mt-3 flex items-center gap-3 border-t border-[#1D2942] pt-4">
                <UserButton
                  appearance={{
                    elements: {
                      avatarBox: "h-10 w-10",
                    },
                  }}
                />

                <span className="text-sm text-slate-300">
                  Account
                </span>
              </div>
            </Show>
          </div>
        </div>
      )}
    </header>
  );
}