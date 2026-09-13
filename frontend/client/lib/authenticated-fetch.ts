"use client";

import { useAuth } from "@clerk/nextjs";

export function useAuthenticatedFetch() {
  const { getToken } = useAuth();

  const fetchApi = async (
    endpoint: string,
    options: RequestInit = {}
  ) => {
    const token = await getToken();

    if (!token) {
      throw new Error("User is not authenticated");
    }

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}${endpoint}`,
      {
        ...options,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
          ...options.headers,
        },
      }
    );

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }

    return response.json();
  };

  return { fetchApi };
}



// ---------------------------------------
//  API USAGE
// ---------------------------------------

// const { fetchApi } = useAuthenticatedFetch();
// const users = await fetchApi("/users");
