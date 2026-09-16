// components/dashboard/DashboardHeader.tsx
"use client";

import { UserButton, useUser } from "@clerk/nextjs";
import { Bell, Sun, Moon } from "lucide-react";

export function DashboardHeader() {
  const { user } = useUser();

  // Fallback for during hydration or if user data isn't ready yet
  const displayName = user?.fullName || user?.username || "User";
  const orgName = user?.organizationMemberships?.[0]?.organization?.name;

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-white/5 bg-[#0B0F19]/80 px-6 backdrop-blur-md">
      <div className="lg:hidden text-white font-bold">SupportFlow AI</div>
      <div className="hidden lg:block" />

      <div className="flex items-center gap-4">
       

        {/* ✅ FIXED: Removed afterSignOutUrl (not supported in Clerk v6) */}
        <UserButton 
          appearance={{
            elements: {
              avatarBox: "h-8 w-8 border border-white/10",
              userButtonPopoverCard: "bg-[#131A2B] border border-white/10",
              userButtonPopoverActionButton: "text-slate-300 hover:bg-white/5 hover:text-white",
              userButtonPopoverFooter: "hidden"
            }
          }}
        >
          <UserButton.MenuItems>
            <UserButton.Action label="manageAccount" />
            <UserButton.Action label="signOut" />
          </UserButton.MenuItems>
        </UserButton>

        {/* User Info Text */}
        <div className="hidden sm:block">
          <p className="text-sm font-medium text-slate-200">{displayName}</p>
          {orgName && <p className="text-[11px] text-slate-500">{orgName}</p>}
        </div>
      </div>
    </header>
  );
}