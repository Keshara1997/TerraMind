
import { AppShell } from "@/components/layout/app-shell";
import MapExplorer from "@/components/maps/map-explorer";

export default function MapPage() {
  return (
    <AppShell>
      <div className="space-y-5">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-400">
            Geospatial workspace
          </p>

          <h1 className="mt-2 text-3xl font-semibold text-white">
            Map Explorer
          </h1>

          <p className="mt-2 text-sm text-slate-400">
            Explore geographical locations and inspect coordinates.
          </p>
        </div>

        <div className="h-[calc(100vh-230px)] min-h-[500px] overflow-hidden rounded-xl border border-white/10 bg-[#111923] p-2">
          <MapExplorer />
        </div>
      </div>
    </AppShell>
  );
}
