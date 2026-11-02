
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  Bot,
  Database,
  FolderKanban,
  Layers3,
  Map,
  Settings,
  Sparkles,
} from "lucide-react";

const navigation = [
  {
    label: "Overview",
    href: "/dashboard",
    icon: Activity,
  },
  {
    label: "Map Explorer",
    href: "/map",
    icon: Map,
  },
  {
    label: "Projects",
    href: "/projects",
    icon: FolderKanban,
  },
  {
    label: "Captures",
    href: "/captures",
    icon: Database,
  },
  {
    label: "AI Assistant",
    href: "/ai",
    icon: Bot,
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-screen w-64 shrink-0 flex-col border-r border-white/10 bg-[#10151d]">
      <div className="flex h-20 items-center gap-3 border-b border-white/10 px-6">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-400 text-slate-950">
          <Layers3 size={22} />
        </div>

        <div>
          <h1 className="text-lg font-bold tracking-tight text-white">
            TerraMind
          </h1>
          <p className="text-[10px] uppercase tracking-[0.2em] text-slate-500">
            Geospatial platform
          </p>
        </div>
      </div>

      <div className="px-4 py-6">
        <p className="mb-3 px-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
          Workspace
        </p>

        <nav className="space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon;
            const active =
              pathname === item.href ||
              (item.href !== "/dashboard" &&
                pathname.startsWith(`${item.href}/`));

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 rounded-lg px-3 py-3 text-sm transition ${
                  active
                    ? "bg-cyan-400/10 font-medium text-cyan-300"
                    : "text-slate-400 hover:bg-white/5 hover:text-white"
                }`}
              >
                <Icon size={18} />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="mt-auto p-4">
        <div className="mb-4 rounded-xl border border-cyan-400/15 bg-cyan-400/5 p-4">
          <Sparkles size={19} className="mb-3 text-cyan-300" />

          <p className="text-sm font-medium text-white">
            Explore with AI
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-400">
            Geospatial intelligence is coming to your workspace.
          </p>
        </div>

        <Link
          href="/settings"
          className="flex items-center gap-3 rounded-lg px-3 py-3 text-sm text-slate-400 hover:bg-white/5 hover:text-white"
        >
          <Settings size={18} />
          Settings
        </Link>
      </div>
    </aside>
  );
}
