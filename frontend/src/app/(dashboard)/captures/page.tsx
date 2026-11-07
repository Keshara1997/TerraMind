"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { captureService, type Capture } from "@/services/capture.service";
import { projectService } from "@/services/project.service";
import { areaService } from "@/services/area.service";
import { AppShell } from "@/components/layout/app-shell";

type Project = {
  id: string;
  name: string;
};

type Area = {
  id: string;
  name: string;
  area_sq_km: number;
};

function statusClass(status: Capture["status"]) {
  switch (status) {
    case "completed":
      return "bg-green-100 text-green-800";
    case "failed":
      return "bg-red-100 text-red-800";
    case "running":
      return "bg-blue-100 text-blue-800";
    default:
      return "bg-gray-100 text-gray-700";
  }
}

function CapturesContent() {
  const [projectId, setProjectId] = useState("");
  const [areaId, setAreaId] = useState("");
  const [message, setMessage] = useState("");

  const projectsQuery = useQuery({
    queryKey: ["projects"],
    queryFn: () => projectService.list(),
  });

  const projects = (projectsQuery.data ?? []) as Project[];

  useEffect(() => {
    if (!projectId && projects.length > 0) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setProjectId(projects[0].id);
    }
  }, [projects, projectId]);

  const areasQuery = useQuery({
    queryKey: ["areas", projectId],
    queryFn: () => areaService.list(projectId),
    enabled: Boolean(projectId),
  });

  const areas = (areasQuery.data ?? []) as Area[];

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setAreaId("");
  }, [projectId]);

  const capturesQuery = useQuery({
    queryKey: ["captures", projectId],
    queryFn: () => captureService.list(projectId),
    enabled: Boolean(projectId),
    refetchInterval: (query) => {
      const captures = query.state.data ?? [];
      return captures.some(
        (capture) =>
          capture.status === "pending" ||
          capture.status === "running",
      )
        ? 3000
        : false;
    },
  });

  const createMutation = useMutation({
    mutationFn: () => captureService.create(projectId, areaId),
    onSuccess: async () => {
      setMessage("Capture submitted successfully.");
      await capturesQuery.refetch();
    },
    onError: () => {
      setMessage("Unable to start the capture. Check the API and worker logs.");
    },
  });

  const captures = capturesQuery.data ?? [];

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-semibold">Geospatial Captures</h1>
        <p className="mt-1 text-sm text-gray-500">
          Start and monitor geospatial data processing jobs.
        </p>
      </div>

      <section className="rounded-xl border bg-white p-5 shadow-sm">
        <h2 className="text-lg font-semibold">Create capture</h2>

        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <div>
            <label className="mb-2 block text-sm font-medium">
              Project
            </label>
            <select
              value={projectId}
              onChange={(event) => setProjectId(event.target.value)}
              className="w-full rounded-lg border p-3"
            >
              <option value="">Select a project</option>
              {projects.map((project) => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium">
              Area
            </label>
            <select
              value={areaId}
              onChange={(event) => setAreaId(event.target.value)}
              className="w-full rounded-lg border p-3"
              disabled={!projectId}
            >
              <option value="">Select an area</option>
              {areas.map((area) => (
                <option key={area.id} value={area.id}>
                  {area.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          type="button"
          disabled={!projectId || !areaId || createMutation.isPending}
          onClick={() => {
            setMessage("");
            createMutation.mutate();
          }}
          className="mt-5 rounded-lg bg-blue-600 px-5 py-3 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          {createMutation.isPending
            ? "Submitting..."
            : "Start capture"}
        </button>

        {message && (
          <p className="mt-3 text-sm text-gray-600">{message}</p>
        )}

        {areasQuery.isLoading && (
          <p className="mt-3 text-sm text-gray-500">Loading areas...</p>
        )}

        {!areasQuery.isLoading && projectId && areas.length === 0 && (
          <p className="mt-3 text-sm text-amber-700">
            This project has no saved areas. Create an area on the map first.
          </p>
        )}
      </section>

      <section className="rounded-xl border bg-white p-5 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Capture history</h2>

          <button
            type="button"
            onClick={() => capturesQuery.refetch()}
            className="rounded-lg border px-3 py-2 text-sm"
          >
            Refresh
          </button>
        </div>

        {capturesQuery.isLoading && (
          <p className="mt-5 text-sm text-gray-500">
            Loading captures...
          </p>
        )}

        {capturesQuery.isError && (
          <p className="mt-5 text-sm text-red-600">
            Unable to load capture history.
          </p>
        )}

        {!capturesQuery.isLoading && captures.length === 0 && (
          <p className="mt-5 text-sm text-gray-500">
            No captures have been created for this project.
          </p>
        )}

        <div className="mt-4 space-y-3">
          {captures.map((capture) => (
            <div
              key={capture.id}
              className="flex flex-col justify-between gap-3 rounded-lg border p-4 md:flex-row md:items-center"
            >
              <div className="min-w-0">
                <p className="break-all text-sm font-medium">
                  {capture.id}
                </p>
                <p className="mt-1 text-xs text-gray-500">
                  Created: {new Date(capture.created_at).toLocaleString()}
                </p>
                {capture.error_message && (
                  <p className="mt-2 text-sm text-red-600">
                    {capture.error_message}
                  </p>
                )}
              </div>

              <span
                className={`w-fit rounded-full px-3 py-1 text-xs font-medium capitalize ${statusClass(capture.status)}`}
              >
                {capture.status}
              </span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default function CapturesPage() {
  return (
    <AppShell>
      <CapturesContent />
    </AppShell>
  );
}