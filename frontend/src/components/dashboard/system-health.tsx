
"use client";

import { useQuery } from "@tanstack/react-query";
import { CheckCircle2, CircleAlert, LoaderCircle } from "lucide-react";

import {
  getApplicationHealth,
  getDatabaseHealth,
  getRedisHealth,
} from "@/services/health.service";

const services = [
  {
    name: "FastAPI Backend",
    queryKey: ["health", "application"],
    queryFn: getApplicationHealth,
  },
  {
    name: "PostgreSQL + PostGIS",
    queryKey: ["health", "database"],
    queryFn: getDatabaseHealth,
  },
  {
    name: "Redis",
    queryKey: ["health", "redis"],
    queryFn: getRedisHealth,
  },
];

export function SystemHealth() {
  return (
    <div className="rounded-xl border border-white/10 bg-[#111923] p-5">
      <div className="mb-5">
        <h2 className="font-semibold text-white">
          System health
        </h2>

        <p className="mt-1 text-xs text-slate-500">
          Live infrastructure connectivity
        </p>
      </div>

      <div className="space-y-5">
        {services.map((service) => (
          <ServiceStatus
            key={service.name}
            service={service}
          />
        ))}
      </div>
    </div>
  );
}

function ServiceStatus({
  service,
}: {
  service: (typeof services)[number];
}) {
  const { data, isLoading, isError } = useQuery({
    queryKey: service.queryKey,
    queryFn: service.queryFn,
    refetchInterval: 30000,
  });

  const healthy = data?.status === "healthy";

  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-slate-300">
        {service.name}
      </span>

      {isLoading ? (
        <span className="flex items-center gap-2 text-xs text-slate-400">
          <LoaderCircle size={14} className="animate-spin" />
          Checking
        </span>
      ) : isError || !healthy ? (
        <span className="flex items-center gap-2 text-xs text-red-400">
          <CircleAlert size={15} />
          Unavailable
        </span>
      ) : (
        <span className="flex items-center gap-2 text-xs text-emerald-400">
          <CheckCircle2 size={15} />
          Healthy
        </span>
      )}
    </div>
  );
}
