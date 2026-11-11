
"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";

import {
  captureService,
  type Capture,
} from "@/services/capture.service";

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

  // Capture configuration
  const [provider, setProvider] = useState<"geojson" | "stac">(
    "geojson",
  );

  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [maxCloudCover, setMaxCloudCover] = useState(30);

  // Fetch projects
  const projectsQuery = useQuery({
    queryKey: ["projects"],
    queryFn: () => projectService.list(),
  });

  const projects = (projectsQuery.data ?? []) as Project[];

  // Select the first project automatically
  useEffect(() => {
    if (!projectId && projects.length > 0) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setProjectId(projects[0].id);
    }
  }, [projects, projectId]);

  // Fetch areas for selected project
  const areasQuery = useQuery({
    queryKey: ["areas", projectId],
    queryFn: () => areaService.list(projectId),
    enabled: Boolean(projectId),
  });

  const areas = (areasQuery.data ?? []) as Area[];

  // Reset selected area when project changes
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setAreaId("");
  }, [projectId]);

  // Fetch capture history
  const capturesQuery = useQuery({
    queryKey: ["captures", projectId],
    queryFn: () => captureService.list(projectId),
    enabled: Boolean(projectId),

    // Automatically refresh while captures are processing
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

  // Create capture mutation
  const createMutation = useMutation({
    mutationFn: () =>
      captureService.create(projectId, areaId, {
        provider,
        startDate,
        endDate,
        maxCloudCover,
      }),

    onSuccess: async () => {
      setMessage("Capture submitted successfully.");
      await capturesQuery.refetch();
    },

    onError: () => {
      setMessage(
        "Unable to start the capture. Check the API and worker logs.",
      );
    },
  });

  const captures = capturesQuery.data ?? [];

  const invalidDateRange =
    provider === "stac" &&
    (
      !startDate ||
      !endDate ||
      startDate > endDate
    );

  const isSubmitDisabled =
    !projectId ||
    !areaId ||
    createMutation.isPending ||
    invalidDateRange;

  return (
    <div className="space-y-6 p-6">

      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-semibold">
          Geospatial Captures
        </h1>

        <p className="mt-1 text-sm text-gray-500">
          Start and monitor geospatial data processing jobs.
        </p>
      </div>

      {/* Create Capture */}
      <section className="rounded-xl border bg-white p-5 shadow-sm">

        <h2 className="text-lg font-semibold">
          Create capture
        </h2>

        <div className="mt-4 grid gap-4 md:grid-cols-2">

          {/* Project Selector */}
          <div>
            <label className="mb-2 block text-sm font-medium">
              Project
            </label>

            <select
              value={projectId}
              onChange={(event) =>
                setProjectId(event.target.value)
              }
              className="w-full rounded-lg border p-3"
            >
              <option value="">
                Select a project
              </option>

              {projects.map((project) => (
                <option
                  key={project.id}
                  value={project.id}
                >
                  {project.name}
                </option>
              ))}
            </select>
          </div>

          {/* Area Selector */}
          <div>
            <label className="mb-2 block text-sm font-medium">
              Area
            </label>

            <select
              value={areaId}
              onChange={(event) =>
                setAreaId(event.target.value)
              }
              className="w-full rounded-lg border p-3"
              disabled={!projectId}
            >
              <option value="">
                Select an area
              </option>

              {areas.map((area) => (
                <option
                  key={area.id}
                  value={area.id}
                >
                  {area.name}
                </option>
              ))}
            </select>
          </div>

          {/* Data Provider */}
          <div>
            <label className="mb-2 block text-sm font-medium">
              Data provider
            </label>

            <select
              value={provider}
              onChange={(event) => {
                setProvider(
                  event.target.value as "geojson" | "stac",
                );
                setMessage("");
              }}
              className="w-full rounded-lg border p-3"
            >
              <option value="geojson">
                Area boundary (GeoJSON)
              </option>

              <option value="stac">
                Sentinel-2 satellite imagery
              </option>
            </select>
          </div>

          {/* Satellite Settings */}
          {provider === "stac" && (
            <>
              {/* Start Date */}
              <div>
                <label className="mb-2 block text-sm font-medium">
                  Start date
                </label>

                <input
                  type="date"
                  value={startDate}
                  onChange={(event) =>
                    setStartDate(event.target.value)
                  }
                  max={endDate || undefined}
                  className="w-full rounded-lg border p-3"
                />
              </div>

              {/* End Date */}
              <div>
                <label className="mb-2 block text-sm font-medium">
                  End date
                </label>

                <input
                  type="date"
                  value={endDate}
                  min={startDate || undefined}
                  max={new Date().toISOString().split("T")[0]}
                  onChange={(event) =>
                    setEndDate(event.target.value)
                  }
                  className="w-full rounded-lg border p-3"
                />
              </div>

              {/* Maximum Cloud Cover */}
              <div className="md:col-span-2">
                <label className="mb-2 block text-sm font-medium">
                  Maximum cloud cover: {maxCloudCover}%
                </label>

                <input
                  type="range"
                  min="0"
                  max="100"
                  step="5"
                  value={maxCloudCover}
                  onChange={(event) =>
                    setMaxCloudCover(
                      Number(event.target.value),
                    )
                  }
                  className="w-full"
                />

                <div className="mt-1 flex justify-between text-xs text-gray-500">
                  <span>0% - Clear sky</span>
                  <span>100% - Fully cloudy</span>
                </div>
              </div>
            </>
          )}

        </div>

        {/* Create Capture Button */}
        <button
          type="button"
          disabled={isSubmitDisabled}
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

        {/* Status Message */}
        {message && (
          <p
            className={`mt-3 text-sm ${
              createMutation.isError
                ? "text-red-600"
                : "text-green-600"
            }`}
          >
            {message}
          </p>
        )}

        {/* Loading Areas */}
        {areasQuery.isLoading && (
          <p className="mt-3 text-sm text-gray-500">
            Loading areas...
          </p>
        )}

        {/* No Areas */}
        {!areasQuery.isLoading &&
          projectId &&
          areas.length === 0 && (
            <p className="mt-3 text-sm text-amber-700">
              This project has no saved areas. Create an area
              on the map first.
            </p>
          )}

        {/* Project Loading Error */}
        {projectsQuery.isError && (
          <p className="mt-3 text-sm text-red-600">
            Unable to load projects.
          </p>
        )}

        {/* Areas Loading Error */}
        {areasQuery.isError && (
          <p className="mt-3 text-sm text-red-600">
            Unable to load project areas.
          </p>
        )}

      </section>

      {/* Capture History */}
      <section className="rounded-xl border bg-white p-5 shadow-sm">

        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">
            Capture history
          </h2>

          <button
            type="button"
            onClick={() => capturesQuery.refetch()}
            disabled={!projectId || capturesQuery.isFetching}
            className="rounded-lg border px-3 py-2 text-sm disabled:opacity-50"
          >
            {capturesQuery.isFetching
              ? "Refreshing..."
              : "Refresh"}
          </button>
        </div>

        {/* Loading */}
        {capturesQuery.isLoading && (
          <p className="mt-5 text-sm text-gray-500">
            Loading captures...
          </p>
        )}

        {/* Error */}
        {capturesQuery.isError && (
          <p className="mt-5 text-sm text-red-600">
            Unable to load capture history.
          </p>
        )}

        {/* Empty State */}
        {!capturesQuery.isLoading &&
          !capturesQuery.isError &&
          captures.length === 0 && (
            <p className="mt-5 text-sm text-gray-500">
              No captures have been created for this project.
            </p>
          )}

        {/* Capture List */}
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
                  Created:{" "}
                  {new Date(
                    capture.created_at,
                  ).toLocaleString()}
                </p>

                {capture.error_message && (
                  <p className="mt-2 text-sm text-red-600">
                    {capture.error_message}
                  </p>
                )}

              </div>

              <span
                className={`w-fit rounded-full px-3 py-1 text-xs font-medium capitalize ${statusClass(
                  capture.status,
                )}`}
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
