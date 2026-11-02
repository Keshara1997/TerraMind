
import type { LucideIcon } from "lucide-react";
import { AppShell } from "./app-shell";

interface PlaceholderPageProps {
  title: string;
  description: string;
  icon: LucideIcon;
}

export function PlaceholderPage({
  title,
  description,
  icon: Icon,
}: PlaceholderPageProps) {
  return (
    <AppShell>
      <div className="mx-auto max-w-5xl space-y-8">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-400">
            Aleph Next workspace
          </p>

          <h1 className="mt-2 text-3xl font-semibold text-white">
            {title}
          </h1>

          <p className="mt-2 text-sm text-slate-400">
            {description}
          </p>
        </div>

        <div className="flex min-h-90 flex-col items-center justify-center rounded-xl border border-dashed border-white/15 bg-[#111923] p-8 text-center">
          <div className="rounded-2xl bg-cyan-400/10 p-5 text-cyan-300">
            <Icon size={34} />
          </div>

          <h2 className="mt-5 text-lg font-semibold text-white">
            Coming in a future development phase
          </h2>

          <p className="mt-2 max-w-md text-sm leading-6 text-slate-400">
            The foundation is ready. We will implement the
            functionality for this module in its dedicated
            development phase.
          </p>
        </div>
      </div>
    </AppShell>
  );
}
