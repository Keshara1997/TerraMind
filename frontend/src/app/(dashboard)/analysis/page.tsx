
"use client";

import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { AppShell } from "@/components/layout/app-shell";
import RasterLayerViewer from "@/components/maps/raster-layer-viewer";
import { projectService } from "@/services/project.service";
import { captureService } from "@/services/capture.service";

type Project = {
  id: string;
  name: string;
};

type Capture = {
  id: string;
  status: string;
};

type Dataset = {
  id: string;
  name: string;
  format: string;
  processing_status: string;
};

function AnalysisContent() {
  const [projectId, setProjectId] = useState("");
  const [captureId, setCaptureId] = useState("");
  const [datasetId, setDatasetId] = useState("");

  const projectsQuery = useQuery({
    queryKey: ["projects"],
    queryFn: () => projectService.list(),
  });

  const projects = (projectsQuery.data ?? []) as Project[];

  useEffect(() => {
    if (!projectId && projects.length > 0) {
      setProjectId(projects[0].id);
    }
  }, [projects, projectId]);

  const capturesQuery = useQuery({
    queryKey: ["captures", projectId],
    queryFn: () => captureService.list(projectId),
    enabled: Boolean(projectId),
  });

  const captures = (capturesQuery.data ?? []) as Capture[];

  const datasetsQuery = useQuery({
    queryKey: ["capture-datasets", projectId, captureId],
    queryFn: () => captureService.getDatasets(projectId, captureId),
    enabled: Boolean(projectId && captureId),
  });

  const datasets = (datasetsQuery.data ?? []) as Dataset[];

  const rasterDatasets = datasets.filter(
    (dataset) =>
      dataset.format === "geotiff" &&
      dataset.processing_status === "completed",
  );

  useEffect(() => {
    setCaptureId("");
    setDatasetId("");
  }, [projectId]);

  useEffect(() => {
    setDatasetId("");
  }, [captureId]);

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-semibold">
          Geospatial Analysis
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Explore processed satellite imagery and NDVI results.
        </p>
      </div>

      <section className="grid gap-4 rounded-xl border bg-white p-5 md:grid-cols-3">
        <div>
          <label className="mb-2 block text-sm font-medium">
            Project
          </label>
          <select
            className="w-full rounded-lg border p-3"
            value={projectId}
            onChange={(event) => setProjectId(event.target.value)}
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
          <label className="mb-2 block text-sm font-medium">
            Capture
          </label>
          <select
            className="w-full rounded-lg border p-3"
            value={captureId}
            onChange={(event) => setCaptureId(event.target.value)}
            disabled={!projectId}
          >
            <option value="">Select capture</option>
            {captures.map((capture) => (
              <option key={capture.id} value={capture.id}>
                {capture.id} ({capture.status})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium">
            Raster dataset
          </label>
          <select
            className="w-full rounded-lg border p-3"
            value={datasetId}
            onChange={(event) => setDatasetId(event.target.value)}
            disabled={!captureId}
          >
            <option value="">Select NDVI dataset</option>
            {rasterDatasets.map((dataset) => (
              <option key={dataset.id} value={dataset.id}>
                {dataset.name}
              </option>
            ))}
          </select>
        </div>
      </section>

      {datasetsQuery.isLoading && captureId && (
        <p className="text-sm text-gray-500">
          Loading datasets...
        </p>
      )}

      {captureId && !datasetsQuery.isLoading &&
        rasterDatasets.length === 0 && (
          <p className="rounded-lg border p-4 text-sm text-gray-500">
            No completed raster datasets are available for this capture.
            Process an NDVI scene first.
          </p>
        )}

      {projectId && captureId && datasetId && (
        <RasterLayerViewer
          projectId={projectId}
          captureId={captureId}
          datasetId={datasetId}
        />
      )}
    </div>
  );
}

export default function AnalysisPage() {
  return (
    <AppShell>
      <AnalysisContent />
    </AppShell>
  );
}
