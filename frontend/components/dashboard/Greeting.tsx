"use client";

import { useEffect, useState } from "react";

interface GreetingProps {
  userName: string;
}

export function Greeting({ userName }: GreetingProps) {
  const [greeting, setGreeting] = useState("Good Morning");

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour >= 12 && hour < 18) setGreeting("Good Afternoon");
    else if (hour >= 18 || hour < 5) setGreeting("Good Evening");
    else setGreeting("Good Morning");
  }, []);

  return (
    <div className="mb-6">
      <h1 className="text-2xl font-bold text-white md:text-3xl">
        {greeting}, {userName} 👋
      </h1>
      <p className="mt-1 text-sm text-slate-400">
        Here's what's happening with your support automation.
      </p>
    </div>
  );
}