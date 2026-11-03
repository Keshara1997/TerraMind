
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { authService } from "@/services/auth.service";

export function ProtectedRoute({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    let mounted = true;

    async function checkAuthentication() {
      try {
        await authService.getCurrentUser();

        if (mounted) {
          setAuthorized(true);
        }
      } catch {
        sessionStorage.removeItem("aleph_access_token");

        if (mounted) {
          router.replace("/login");
        }
      }
    }

    checkAuthentication();

    return () => {
      mounted = false;
    };
  }, [router]);

  if (!authorized) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#0b1017] text-slate-400">
        Checking your session...
      </div>
    );
  }

  return children;
}
