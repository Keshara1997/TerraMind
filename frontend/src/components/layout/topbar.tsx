
"use client";

import { Bell, Search, CircleHelp } from "lucide-react";

export function Topbar() {
  return (
    <header className="flex h-16 items-center justify-between border-b border-white/10 bg-[#10151d] px-6">
      <div>
        <p className="text-sm text-slate-400">
          Workspace /{" "}
          <span className="text-white">Overview</span>
        </p>
      </div>

      <div className="flex items-center gap-4">
        <div className="hidden items-center gap-2 rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 md:flex">
          <Search size={15} className="text-slate-500" />

          <input
            placeholder="Search workspace..."
            className="w-40 bg-transparent text-xs text-white outline-none placeholder:text-slate-500"
          />

          <kbd className="rounded border border-white/10 px-1.5 py-0.5 text-[10px] text-slate-500">
            /
          </kbd>
        </div>

        <button
          aria-label="Notifications"
          className="rounded-lg p-2 text-slate-400 hover:bg-white/5 hover:text-white"
        >
          <Bell size={18} />
        </button>

        <button
          aria-label="Help"
          className="rounded-lg p-2 text-slate-400 hover:bg-white/5 hover:text-white"
        >
          <CircleHelp size={18} />
        </button>

        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-cyan-400/15 text-xs font-bold text-cyan-300">
          AN
        </div>
      </div>
    </header>
  );
}
