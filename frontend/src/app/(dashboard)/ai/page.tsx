"use client";

import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import GeospatialAssistant from "@/components/ai/geospatial-assistant";
import { AppShell } from "@/components/layout/app-shell";

import { projectService } from "@/services/project.service";
import { aiService } from "@/services/ai.service";

export default function AIPage() {
  const [projectId, setProjectId] = useState("");
  const [startDate, setStartDate] = useState("2026-01-01");
  const [endDate, setEndDate] = useState("2026-10-31");
  const [report, setReport] = useState("");
  const [reportLoading, setReportLoading] = useState(false);
  const [reportError, setReportError] = useState("");

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

  async function generateReport() {
    if (!projectId || reportLoading) return;

    setReportLoading(true);
    setReportError("");
    setReport("");

    try {
      const result = await aiService.generateReport(
        projectId,
        startDate,
        endDate,
      );

      setReport(result.report);
    } catch {
      setReportError("Unable to generate the environmental report.");
    } finally {
      setReportLoading(false);
    }
  }

  return (
    <AppShell>
      <div className="space-y-6 p-6">
        <div>
          <h1 className="text-2xl font-semibold">
            AI Geospatial Analysis
          </h1>

          <p className="mt-1 text-sm text-gray-500">
            Explore satellite observations using natural language.
          </p>
        </div>

        <section className="rounded-xl border p-5">
          <label className="mb-2 block text-sm font-medium">
            Select project
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

          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <div>
              <label className="mb-2 block text-sm font-medium">
                Start date
              </label>

              <input
                type="date"
                value={startDate}
                onChange={(event) => setStartDate(event.target.value)}
                className="w-full rounded-lg border p-3"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium">
                End date
              </label>

              <input
                type="date"
                value={endDate}
                onChange={(event) => setEndDate(event.target.value)}
                className="w-full rounded-lg border p-3"
              />
            </div>
          </div>
        </section>

        {projectId && (
          <GeospatialAssistant projectId={projectId} />
        )}

        <section className="rounded-xl border p-5">
          <h2 className="text-lg font-semibold">
            Environmental Report
          </h2>

          <p className="mt-1 text-sm text-gray-500">
            Generate an evidence-based report for the selected period.
          </p>

          <button
            type="button"
            onClick={() => void generateReport()}
            disabled={!projectId || reportLoading}
            className="mt-4 rounded-lg bg-blue-600 px-5 py-3 text-sm font-medium text-white disabled:opacity-50"
          >
            {reportLoading ? "Generating..." : "Generate report"}
          </button>

          {reportError && (
            <p className="mt-3 text-sm text-red-600">
              {reportError}
            </p>
          )}

          {report && (
            <article className="mt-5 whitespace-pre-wrap rounded-lg bg-gray-50 p-5 text-sm leading-7">
              {report}
            </article>
          )}
        </section>
      </div>
    </AppShell>
  );
}