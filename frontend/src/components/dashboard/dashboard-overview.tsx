
"use client";

import {
  Activity,
  Database,
  FolderKanban,
  Globe2,
  MapPinned,
  Plus,
  ArrowUpRight,
} from "lucide-react";

import Link from "next/link";
import { SystemHealth } from "./system-health";
import { useMapStore } from "@/store/map.store";
import { StatCard } from "./stats-cards";
import MapExplorer from "../maps/map-explorer";

export function DashboardOverview() {
  const latitude = useMapStore(
    (state) => state.selectedLatitude,
  );

  const longitude = useMapStore(
    (state) => state.selectedLongitude,
  );

  return (
    <div className="mx-auto max-w-[1600px] space-y-7">
      <section className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-400">
            Geospatial workspace
          </p>

          <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white">
            Overview
          </h1>

          <p className="mt-2 text-sm text-slate-400">
            Explore, collect and understand geographical data.
          </p>
        </div>

        <Link
          href="/map"
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-cyan-400 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
        >
          <Plus size={17} />
          Explore map
        </Link>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          title="Projects"
          value="0"
          description="No projects created yet"
          icon={FolderKanban}
        />

        <StatCard
          title="Data captures"
          value="0"
          description="No capture jobs yet"
          icon={Database}
        />

        <StatCard
          title="Geographic areas"
          value="0"
          description="Waiting for your first selection"
          icon={Globe2}
        />

        <StatCard
          title="System services"
          value="3"
          description="Backend, database and cache"
          icon={Activity}
        />
      </section>

      <section className="grid gap-5 xl:grid-cols-[minmax(0,1.8fr)_minmax(300px,0.8fr)]">
        <div className="overflow-hidden rounded-xl border border-white/10 bg-[#111923]">
          <div className="flex items-center justify-between border-b border-white/10 p-5">
            <div>
              <h2 className="font-semibold text-white">
                Map explorer
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Select a location to inspect its coordinates
              </p>
            </div>

            <MapPinned size={19} className="text-cyan-300" />
          </div>

          <div className="h-[440px] p-2">
            <MapExplorer />
          </div>

          <div className="flex flex-wrap items-center justify-between gap-2 border-t border-white/10 px-5 py-4">
            <div className="text-xs text-slate-400">
              {latitude !== null && longitude !== null
                ? `Selected: ${latitude.toFixed(5)}, ${longitude.toFixed(5)}`
                : "Click anywhere on the map to select a location"}
            </div>

            <Link
              href="/map"
              className="flex items-center gap-1 text-xs font-medium text-cyan-300 hover:text-cyan-200"
            >
              Open explorer
              <ArrowUpRight size={14} />
            </Link>
          </div>
        </div>

        <div className="space-y-5">
          <SystemHealth />

          <div className="rounded-xl border border-white/10 bg-[#111923] p-5">
            <div className="flex items-center gap-2">
              <Globe2 size={19} className="text-cyan-300" />

              <h2 className="font-semibold text-white">
                Getting started
              </h2>
            </div>

            <div className="mt-5 space-y-4">
              {[
                "Explore a geographical location",
                "Create your first project",
                "Select an area for data collection",
                "Generate your first dataset",
              ].map((item, index) => (
                <div key={item} className="flex items-start gap-3">
                  <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-white/10 text-xs text-cyan-300">
                    {index + 1}
                  </span>

                  <p className="pt-1 text-sm text-slate-400">
                    {item}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <footer className="border-t border-white/10 pt-5 text-xs text-slate-600">
        Aleph Next · Geospatial exploration platform · Development 0.1.0
      </footer>
    </div>
  );
}
