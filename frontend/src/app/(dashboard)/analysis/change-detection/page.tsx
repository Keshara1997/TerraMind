"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";

import { AppShell } from "@/components/layout/app-shell";

import {
  analysisService,
  type NDVITimeSeriesPoint,
} from "@/services/analysis.service";
import { projectService } from "@/services/project.service";

export default function ChangeDetectionPage() {
  const [projectId, setProjectId] = useState("");
  const [beforeDatasetId, setBeforeDatasetId] = useState("");
  const [afterDatasetId, setAfterDatasetId] = useState("");
  const [threshold, setThreshold] = useState(0.1);

  const projectsQuery = useQuery({
    queryKey: ["projects"],
    queryFn: () => projectService.list(),
  });

  const projects = projectsQuery.data ?? [];

  useEffect(() => {
    if (!projectId && projects.length > 0) {
      setProjectId(projects[0].id);
    }
  }, [projects, projectId]);

  const seriesQuery = useQuery({
    queryKey: ["ndvi-time-series-for-change", projectId],
    queryFn: () => analysisService.getNDVITimeSeries(projectId),
    enabled: Boolean(projectId),
  });

  const ndviPoints: NDVITimeSeriesPoint[] = seriesQuery.data?.points ?? [];

  const changeMutation = useMutation({
    mutationFn: () =>
      analysisService.createNDVIChange(
        projectId,
        beforeDatasetId,
        afterDatasetId,
        threshold,
      ),
  });

  return (
    <AppShell>
      <div className="space-y-6 p-6">
        <div>
          <h1 className="text-2xl font-semibold">NDVI Change Detection</h1>
          <p className="mt-1 text-sm text-gray-500">
            Compare two completed NDVI rasters to detect vegetation gain or loss.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="mb-2 block text-sm font-medium">Project</label>
            <select
              className="w-full rounded-lg border p-3"
              value={projectId}
              onChange={(event) => {
                setProjectId(event.target.value);
                setBeforeDatasetId("");
                setAfterDatasetId("");
              }}
            >
              <option value="">Select project</option>
              {projects.map((project) => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium">Threshold</label>
            <input
              type="number"
              min={0.01}
              max={1}
              step={0.01}
              className="w-full rounded-lg border p-3"
              value={threshold}
              onChange={(event) => setThreshold(Number(event.target.value))}
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium">Before NDVI</label>
            <select
              className="w-full rounded-lg border p-3"
              value={beforeDatasetId}
              onChange={(event) => setBeforeDatasetId(event.target.value)}
              disabled={!ndviPoints.length}
            >
              <option value="">Select dataset</option>
              {ndviPoints.map((point) => (
                <option key={point.dataset_id} value={point.dataset_id}>
                  {point.acquisition_date} — mean{" "}
                  {point.mean?.toFixed(3) ?? "N/A"}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium">After NDVI</label>
            <select
              className="w-full rounded-lg border p-3"
              value={afterDatasetId}
              onChange={(event) => setAfterDatasetId(event.target.value)}
              disabled={!ndviPoints.length}
            >
              <option value="">Select dataset</option>
              {ndviPoints.map((point) => (
                <option key={point.dataset_id} value={point.dataset_id}>
                  {point.acquisition_date} — mean{" "}
                  {point.mean?.toFixed(3) ?? "N/A"}
                </option>
              ))}
            </select>
          </div>
        </div>

        {seriesQuery.isLoading && <p>Loading NDVI datasets...</p>}

        {seriesQuery.isError && (
          <p className="text-sm text-red-600">
            Unable to load NDVI datasets for this project.
          </p>
        )}

        <button
          type="button"
          className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
          disabled={
            !projectId ||
            !beforeDatasetId ||
            !afterDatasetId ||
            beforeDatasetId === afterDatasetId ||
            changeMutation.isPending
          }
          onClick={() => changeMutation.mutate()}
        >
          {changeMutation.isPending ? "Queuing..." : "Run change detection"}
        </button>

        {changeMutation.isSuccess && (
          <div className="rounded-xl border border-emerald-500/40 bg-emerald-500/10 p-4 text-sm">
            <p className="font-medium">Job queued</p>
            <p className="mt-1 text-gray-300">
              Output dataset: {changeMutation.data.dataset_id} (
              {changeMutation.data.status})
            </p>
            <p className="mt-1 text-gray-400">{changeMutation.data.message}</p>
          </div>
        )}

        {changeMutation.isError && (
          <p className="text-sm text-red-600">
            Change detection request failed. Check the API and worker logs.
          </p>
        )}
      </div>
    </AppShell>
  );
}