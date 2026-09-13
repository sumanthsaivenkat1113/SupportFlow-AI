"use client";

import { UserButton } from "@clerk/nextjs";

export default function DashBoradPage() {
    return (
        <>
            <UserButton>
                <UserButton.MenuItems>
                    <UserButton.Action label="manageAccount" />
                    <UserButton.Action label="signOut" />
                </UserButton.MenuItems>
            </UserButton>
            <h2>
                this is Dashboard page
            </h2>
        </>
    )
}