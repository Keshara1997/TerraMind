
"use client";

import { useEffect, useState } from "react";
import { authService } from "@/services/auth.service";

export function AuthProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    let mounted = true;

    async function initialize() {
      const hasToken = sessionStorage.getItem("aleph_access_token");

      if (!hasToken) {
        await authService.refresh();
      }

      if (mounted) {
        setInitialized(true);
      }
    }

    initialize();

    return () => {
      mounted = false;
    };
  }, []);

  if (!initialized) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#0b1017] text-slate-400">
        Loading Aleph Next...
      </div>
    );
  }

  return children;
}

