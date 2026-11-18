"use client";

import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import NDVITimeSeriesChart from "@/components/analysis/ndvi-time-series-chart";
import { AppShell } from "@/components/layout/app-shell";

import { projectService } from "@/services/project.service";
import { analysisService } from "@/services/analysis.service";

export default function TimeSeriesPage() {
  const [projectId, setProjectId] = useState("");
  const [startDate, setStartDate] = useState("2026-01-01");
  const [endDate, setEndDate] = useState("2026-10-31");

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
    queryKey: ["ndvi-time-series", projectId, startDate, endDate],
    queryFn: () =>
      analysisService.getNDVITimeSeries(
        projectId,
        startDate,
        endDate,
      ),
    enabled: Boolean(projectId),
  });

  const series = seriesQuery.data;

  return (
    <AppShell>
      <div className="space-y-6 p-6">
        <div>
          <h1 className="text-2xl font-semibold">
            NDVI Time-Series Analysis
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Track vegetation changes across satellite acquisition dates.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
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
              Start date
            </label>

            <input
              type="date"
              className="w-full rounded-lg border p-3"
              value={startDate}
              onChange={(event) => setStartDate(event.target.value)}
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium">
              End date
            </label>

            <input
              type="date"
              className="w-full rounded-lg border p-3"
              value={endDate}
              onChange={(event) => setEndDate(event.target.value)}
            />
          </div>
        </div>

        {seriesQuery.isLoading && (
          <p>Loading NDVI observations...</p>
        )}

        {seriesQuery.isError && (
          <p className="text-sm text-red-600">
            Unable to load the NDVI time series.
          </p>
        )}

        {series && (
          <>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-xl border p-5">
                <p className="text-sm text-gray-500">
                  Total observations
                </p>
                <p className="mt-2 text-3xl font-semibold">
                  {series.total_observations}
                </p>
              </div>

              <div className="rounded-xl border p-5">
                <p className="text-sm text-gray-500">
                  Latest mean NDVI
                </p>
                <p className="mt-2 text-3xl font-semibold">
                  {series.points.length > 0
                    ? series.points.at(-1)?.mean?.toFixed(3) ?? "N/A"
                    : "N/A"}
                </p>
              </div>
            </div>

            <section className="rounded-xl border p-5">
              <h2 className="mb-4 text-lg font-semibold">
                Vegetation index over time
              </h2>

              <NDVITimeSeriesChart points={series.points} />
            </section>

            <section className="rounded-xl border p-5">
              <h2 className="mb-4 text-lg font-semibold">
                Observation history
              </h2>

              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-left">
                      <th className="p-3">Acquisition date</th>
                      <th className="p-3">Mean</th>
                      <th className="p-3">Median</th>
                      <th className="p-3">Minimum</th>
                      <th className="p-3">Maximum</th>
                    </tr>
                  </thead>

                  <tbody>
                    {series.points.map((point) => (
                      <tr
                        key={point.dataset_id}
                        className="border-b"
                      >
                        <td className="p-3">
                          {point.acquisition_date}
                        </td>
                        <td className="p-3">
                          {point.mean?.toFixed(3) ?? "N/A"}
                        </td>
                        <td className="p-3">
                          {point.median?.toFixed(3) ?? "N/A"}
                        </td>
                        <td className="p-3">
                          {point.minimum?.toFixed(3) ?? "N/A"}
                        </td>
                        <td className="p-3">
                          {point.maximum?.toFixed(3) ?? "N/A"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        )}
      </div>
    </AppShell>
  );
}