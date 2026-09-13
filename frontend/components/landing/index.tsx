"use client";

import { useState } from "react";

import Navbar from "@/components/landing/Navbar";
import Hero from "@/components/landing/Hero";
import ValueStrip from "@/components/landing/ValueStrip";
import Features from "@/components/landing/Features";
import Workflow from "@/components/landing/Workflow";
import KnowledgeSection from "@/components/landing/KnowledgeSection";
import DecisionSection from "@/components/landing/DecisionSection";
import ExportSection from "@/components/landing/ExportSection";
import FAQ from "@/components/landing/FAQ";
import FinalCTA from "@/components/landing/FinalCTA";
import Footer from "@/components/landing/Footer";
import BackgroundGlow from "@/components/landing/BackgroundGlow";

export default function Landing() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const scrollTo = (id: string) => {
    setMobileOpen(false);

    document.getElementById(id)?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  };

  return (
    <main
      className="min-h-screen overflow-x-hidden"
      style={{
        background: "#050816",
        color: "#F8FAFC",
        fontFamily:
          "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
      }}
    >
      <BackgroundGlow />

      <Navbar
        mobileOpen={mobileOpen}
        setMobileOpen={setMobileOpen}
        scrollTo={scrollTo}
      />

      <Hero scrollTo={scrollTo} />

      <ValueStrip />

      <Features />

      <Workflow />

      <KnowledgeSection />

      <DecisionSection />

      <ExportSection />

      <FAQ
        openFaq={openFaq}
        setOpenFaq={setOpenFaq}
      />

      <FinalCTA />

      <Footer scrollTo={scrollTo} />
    </main>
  );
}