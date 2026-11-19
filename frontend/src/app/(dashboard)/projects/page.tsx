"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FolderKanban, Plus } from "lucide-react";
import Link from "next/link";

import { AppShell } from "@/components/layout/app-shell";
import { projectService } from "@/services/project.service";

export default function ProjectsPage() {
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  const projectsQuery = useQuery({
    queryKey: ["projects"],
    queryFn: () => projectService.list(),
  });

  const createMutation = useMutation({
    mutationFn: () =>
      projectService.create({
        name: name.trim(),
        description: description.trim() || null,
      }),
    onSuccess: () => {
      setName("");
      setDescription("");
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });

  const projects = projectsQuery.data ?? [];

  return (
    <AppShell>
      <div className="mx-auto max-w-4xl space-y-8 p-6">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-400">
              Workspace
            </p>
            <h1 className="text-2xl font-semibold text-white">Projects</h1>
            <p className="mt-1 text-sm text-slate-400">
              Create and manage geospatial projects for areas and captures.
            </p>
          </div>
          <Link
            href="/map"
            className="inline-flex items-center gap-2 text-sm text-cyan-300 hover:text-cyan-200"
          >
            <FolderKanban size={16} />
            Open map editor
          </Link>
        </div>

        <form
          className="space-y-4 rounded-xl border border-white/10 bg-[#111923] p-5"
          onSubmit={(event) => {
            event.preventDefault();
            if (name.trim()) {
              createMutation.mutate();
            }
          }}
        >
          <h2 className="text-sm font-semibold text-white">New project</h2>
          <input
            className="w-full rounded-lg border border-white/10 bg-black/20 p-3 text-white"
            placeholder="Project name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            required
          />
          <textarea
            className="w-full rounded-lg border border-white/10 bg-black/20 p-3 text-white"
            placeholder="Description (optional)"
            rows={2}
            value={description}
            onChange={(event) => setDescription(event.target.value)}
          />
          <button
            type="submit"
            disabled={createMutation.isPending || !name.trim()}
            className="inline-flex items-center gap-2 rounded-lg bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 disabled:opacity-50"
          >
            <Plus size={16} />
            Create project
          </button>
          {createMutation.isError && (
            <p className="text-sm text-red-400">Could not create project.</p>
          )}
        </form>

        <section className="rounded-xl border border-white/10 bg-[#111923] p-5">
          <h2 className="text-sm font-semibold text-white">Your projects</h2>

          {projectsQuery.isLoading && (
            <p className="mt-4 text-sm text-slate-400">Loading...</p>
          )}

          {projectsQuery.isError && (
            <p className="mt-4 text-sm text-red-400">
              Sign in to load projects.
            </p>
          )}

          {projects.length === 0 && !projectsQuery.isLoading && (
            <p className="mt-4 text-sm text-slate-400">
              No projects yet. Create one above or from the map page.
            </p>
          )}

          <ul className="mt-4 divide-y divide-white/10">
            {projects.map((project) => (
              <li
                key={project.id}
                className="flex flex-col gap-1 py-4 sm:flex-row sm:items-center sm:justify-between"
              >
                <div>
                  <p className="font-medium text-white">{project.name}</p>
                  {project.description && (
                    <p className="text-sm text-slate-400">
                      {project.description}
                    </p>
                  )}
                  <p className="text-xs text-slate-500">
                    Status: {project.status}
                  </p>
                </div>
                <Link
                  href={`/map?project=${project.id}`}
                  className="text-sm text-cyan-300 hover:underline"
                >
                  Edit areas
                </Link>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </AppShell>
  );
}