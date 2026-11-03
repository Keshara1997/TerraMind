"use client";

import { useRouter } from "next/navigation";
import { authService } from "@/services/auth.service";

export function LogoutButton() {
  const router = useRouter();

  async function handleLogout() {
    await authService.logout();
    router.replace("/login");
  }

  return (
    <button
      type="button"
      onClick={handleLogout}
      className="rounded-lg border border-white/10 px-4 py-2 text-sm text-slate-300 hover:bg-white/5"
    >
      Sign out
    </button>
  );
}