
"use client";

import { UserButton, useAuth } from "@clerk/nextjs";
import { useEffect, useState } from "react";

interface User {
    id: string;
    clerk_id: string;
    name: string | null;
    email: string;
    img_url: string | null;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export default function DashBoradPage() {
    const { getToken, isLoaded, isSignedIn } = useAuth();

    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!isLoaded || !isSignedIn) return;

        const syncUser = async () => {
            try {
                const token = await getToken();

                if (!token) {
                    throw new Error("No authentication token");
                }

                const response = await fetch(`${API_URL}/api/users/me`, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });

                if (!response.ok) {
                    throw new Error("Failed to sync user");
                }

                const data = await response.json();

                setUser(data);
            } catch (error) {
                console.error("User sync failed:", error);
            } finally {
                setLoading(false);
            }
        };

        syncUser();
    }, [isLoaded, isSignedIn, getToken]);

    if (!isLoaded || loading) {
        return <div>Loading...</div>;
    }

    return (
        <main>
            <div>
                <UserButton>
                    <UserButton.MenuItems>
                        <UserButton.Action label="manageAccount" />
                        <UserButton.Action label="signOut" />
                    </UserButton.MenuItems>
                </UserButton>
            </div>

            <h2>Dashboard</h2>

            {user && (
                <div>
                    <p>Welcome, {user.name}</p>
                    <p>{user.email}</p>
                    <p>Clerk ID: {user.clerk_id}</p>
                </div>
            )}
        </main>
    );
}

