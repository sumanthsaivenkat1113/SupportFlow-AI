import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merges Tailwind CSS classes conditionally.
 * Combines clsx for conditional logic and tailwind-merge for conflict resolution.
 * 
 * @example
 * cn("px-2 py-1", isActive && "bg-blue-500", "px-4")
 * // => "py-1 bg-blue-500 px-4" (px-4 overrides px-2)
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}