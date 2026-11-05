
"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  LngLatBounds,
  Map as MapLibre,
  NavigationControl,
} from "maplibre-gl";
import type { GeoJSONSource, Map as MapInstance } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import type {
  Feature,
  FeatureCollection,
  Geometry,
  Position,
} from "geojson";

import { areaService, type Area } from "@/services/area.service";
import { projectService, type Project } from "@/services/project.service";

const EMPTY_COLLECTION: FeatureCollection = {
  type: "FeatureCollection",
  features: [],
};

function createDraftFeature(
  coordinates: Position[],
): FeatureCollection {
  if (coordinates.length === 0) {
    return EMPTY_COLLECTION;
  }

  let geometry: Geometry;

  if (coordinates.length === 1) {
    geometry = {
      type: "Point",
      coordinates: coordinates[0],
    };
  } else if (coordinates.length === 2) {
    geometry = {
      type: "LineString",
      coordinates,
    };
  } else {
    const ring = [
      ...coordinates,
      coordinates[0],
    ];

    geometry = {
      type: "Polygon",
      coordinates: [ring],
    };
  }

  return {
    type: "FeatureCollection",
    features: [
      {
        type: "Feature",
        properties: {},
        geometry,
      },
    ],
  };
}

function createSavedFeatures(
  areas: Area[],
): FeatureCollection {
  return {
    type: "FeatureCollection",
    features: areas.map((area) => ({
      type: "Feature",
      properties: {
        id: area.id,
        name: area.name,
      },
      geometry: area.geometry as Geometry,
    })),
  };
}

export default function AreaEditor() {
  const mapContainer = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MapInstance | null>(null);
  const draftRef = useRef<Position[]>([]);
  const drawingRef = useRef(false);

  const [mapLoaded, setMapLoaded] = useState(false);
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectId, setProjectId] = useState("");
  const [areas, setAreas] = useState<Area[]>([]);
  const [draft, setDraft] = useState<Position[]>([]);
  const [drawing, setDrawing] = useState(false);
  const [areaName, setAreaName] = useState("");
  const [description, setDescription] = useState("");
  const [newProjectName, setNewProjectName] = useState("");
  const [selectedArea, setSelectedArea] = useState<Area | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const updateDraft = useCallback((coordinates: Position[]) => {
    draftRef.current = coordinates;
    setDraft(coordinates);

    const source = mapRef.current?.getSource(
      "draft-area",
    ) as GeoJSONSource | undefined;

    source?.setData(createDraftFeature(coordinates));
  }, []);

  const loadAreas = useCallback(async (id: string) => {
    if (!id) {
      setAreas([]);
      return;
    }

    const data = await areaService.list(id);
    setAreas(data);
    setSelectedArea(null);
  }, []);

  useEffect(() => {
    let mounted = true;

    async function loadProjects() {
      try {
        const data = await projectService.list();

        if (!mounted) return;

        setProjects(data);

        if (data.length > 0) {
          setProjectId(data[0].id);
        }
      } catch {
        if (mounted) {
          setError("Could not load projects. Please sign in again.");
        }
      }
    }

    loadProjects();

    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    if (!projectId) return;

    let mounted = true;

    async function refresh() {
      setLoading(true);
      setError("");

      try {
        const data = await areaService.list(projectId);

        if (mounted) {
          setAreas(data);
          setSelectedArea(null);
        }
      } catch {
        if (mounted) {
          setError("Unable to load areas for this project.");
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    refresh();

    return () => {
      mounted = false;
    };
  }, [projectId]);

  useEffect(() => {
    if (!mapContainer.current || mapRef.current) return;

    const map = new MapLibre({
      container: mapContainer.current,
      style:
        process.env.NEXT_PUBLIC_MAP_STYLE_URL ??
        "https://tiles.openfreemap.org/styles/liberty",
      center: [79.8612, 6.9271],
      zoom: 10,
    });

    mapRef.current = map;
    map.addControl(new NavigationControl(), "top-right");

    map.on("load", () => {
      map.addSource("saved-areas", {
        type: "geojson",
        data: EMPTY_COLLECTION,
      });

      map.addLayer({
        id: "saved-area-fill",
        type: "fill",
        source: "saved-areas",
        paint: {
          "fill-color": "#06b6d4",
          "fill-opacity": 0.25,
        },
      });

      map.addLayer({
        id: "saved-area-outline",
        type: "line",
        source: "saved-areas",
        paint: {
          "line-color": "#22d3ee",
          "line-width": 2,
        },
      });

      map.addSource("draft-area", {
        type: "geojson",
        data: EMPTY_COLLECTION,
      });

      map.addLayer({
        id: "draft-area-fill",
        type: "fill",
        source: "draft-area",
        filter: ["==", ["geometry-type"], "Polygon"],
        paint: {
          "fill-color": "#f59e0b",
          "fill-opacity": 0.25,
        },
      });

      map.addLayer({
        id: "draft-area-line",
        type: "line",
        source: "draft-area",
        paint: {
          "line-color": "#fbbf24",
          "line-width": 3,
        },
      });

      map.addLayer({
        id: "draft-area-points",
        type: "circle",
        source: "draft-area",
        filter: ["==", ["geometry-type"], "Point"],
        paint: {
          "circle-radius": 6,
          "circle-color": "#f59e0b",
          "circle-stroke-width": 2,
          "circle-stroke-color": "#ffffff",
        },
      });

      setMapLoaded(true);
    });

    map.on("click", (event) => {
      if (!drawingRef.current) return;

      const nextCoordinates: Position[] = [
        ...draftRef.current,
        [event.lngLat.lng, event.lngLat.lat],
      ];

      updateDraft(nextCoordinates);
    });

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, [updateDraft]);

  useEffect(() => {
    if (!mapLoaded) return;

    const source = mapRef.current?.getSource(
      "saved-areas",
    ) as GeoJSONSource | undefined;

    source?.setData(createSavedFeatures(areas));
  }, [areas, mapLoaded]);

  async function handleCreateProject() {
    if (newProjectName.trim().length < 2) {
      setError("Enter a project name with at least two characters.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const project = await projectService.create({
        name: newProjectName.trim(),
      });

      setProjects((previous) => [project, ...previous]);
      setProjectId(project.id);
      setNewProjectName("");
      setMessage("Project created successfully.");
    } catch {
      setError("Unable to create the project.");
    } finally {
      setLoading(false);
    }
  }

  function startDrawing() {
    if (!projectId) {
      setError("Create or select a project first.");
      return;
    }

    draftRef.current = [];
    setDraft([]);
    setAreaName("");
    setDescription("");
    setError("");
    setMessage("");

    drawingRef.current = true;
    setDrawing(true);

    const source = mapRef.current?.getSource(
      "draft-area",
    ) as GeoJSONSource | undefined;

    source?.setData(EMPTY_COLLECTION);
  }

  function finishDrawing() {
    drawingRef.current = false;
    setDrawing(false);

    if (draftRef.current.length < 3) {
      setError("A polygon needs at least three vertices.");
      return;
    }

    setMessage("Polygon ready. Enter a name and save it.");
  }

  function cancelDrawing() {
    drawingRef.current = false;
    setDrawing(false);
    updateDraft([]);
    setError("");
    setMessage("");
  }

  async function saveArea() {
    if (!projectId) return;

    if (areaName.trim().length < 2) {
      setError("Enter an area name.");
      return;
    }

    if (draft.length < 3) {
      setError("Draw at least three points on the map.");
      return;
    }

    const ring = [...draft, draft[0]];

    const geometry = {
      type: "Polygon" as const,
      coordinates: [ring],
    };

    setLoading(true);
    setError("");

    try {
      const created = await areaService.create(projectId, {
        name: areaName.trim(),
        description: description.trim() || null,
        geometry,
      });

      setAreas((previous) => [created, ...previous]);
      setSelectedArea(created);
      updateDraft([]);
      setMessage("Area saved successfully.");
      setAreaName("");
      setDescription("");
    } catch (err) {
      const detail = (
        err as {
          response?: { data?: { detail?: string } };
        }
      ).response?.data?.detail;

      setError(
        typeof detail === "string"
          ? detail
          : "Unable to save area. Check the polygon geometry.",
      );
    } finally {
      setLoading(false);
    }
  }

  async function deleteArea(area: Area) {
    if (!projectId) return;

    if (!window.confirm(`Delete "${area.name}"?`)) return;

    setLoading(true);
    setError("");

    try {
      await areaService.delete(projectId, area.id);

      setAreas((previous) =>
        previous.filter((item) => item.id !== area.id),
      );

      if (selectedArea?.id === area.id) {
        setSelectedArea(null);
      }

      setMessage("Area deleted.");
    } catch {
      setError("Unable to delete this area.");
    } finally {
      setLoading(false);
    }
  }

  function selectArea(area: Area) {
    setSelectedArea(area);

    const coordinates =
      area.geometry.type === "Polygon"
        ? area.geometry.coordinates[0]
        : area.geometry.coordinates[0][0];

    if (coordinates.length > 0) {
      const bounds = new LngLatBounds();

      coordinates.forEach((coordinate) => {
        bounds.extend([
          coordinate[0],
          coordinate[1],
        ]);
      });

      mapRef.current?.fitBounds(bounds, {
        padding: 60,
        maxZoom: 15,
      });
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white">
            Area Explorer
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Draw, save, and manage spatial boundaries.
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          {!drawing ? (
            <button
              type="button"
              onClick={startDrawing}
              disabled={!projectId || loading}
              className="rounded-lg bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950 disabled:opacity-50"
            >
              Draw polygon
            </button>
          ) : (
            <>
              <button
                type="button"
                onClick={finishDrawing}
                className="rounded-lg bg-amber-400 px-4 py-2 text-sm font-semibold text-slate-950"
              >
                Finish polygon
              </button>

              <button
                type="button"
                onClick={cancelDrawing}
                className="rounded-lg border border-white/10 px-4 py-2 text-sm text-white"
              >
                Cancel
              </button>
            </>
          )}
        </div>
      </div>

      {error && (
        <p role="alert" className="rounded-lg bg-red-500/10 p-3 text-sm text-red-400">
          {error}
        </p>
      )}

      {message && (
        <p role="status" className="rounded-lg bg-emerald-500/10 p-3 text-sm text-emerald-400">
          {message}
        </p>
      )}

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_340px]">
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-3 rounded-xl border border-white/10 bg-[#111923] p-3">
            <label
              htmlFor="project"
              className="text-sm text-slate-400"
            >
              Project
            </label>

            <select
              id="project"
              value={projectId}
              onChange={(event) => setProjectId(event.target.value)}
              className="min-w-0 flex-1 rounded-lg border border-white/10 bg-[#0b1017] px-3 py-2 text-sm text-white"
            >
              <option value="">Select a project</option>
              {projects.map((project) => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
          </div>

          <div className="relative h-[600px] overflow-hidden rounded-xl border border-white/10">
            <div
              ref={mapContainer}
              className="h-full w-full"
            />

            {drawing && (
              <div className="absolute left-3 top-3 rounded-lg bg-[#111923]/95 px-3 py-2 text-xs text-amber-300 shadow-lg">
                Click the map to add polygon vertices · {draft.length} points
              </div>
            )}
          </div>
        </div>

        <aside className="space-y-4">
          {!projectId && (
            <div className="rounded-xl border border-white/10 bg-[#111923] p-4">
              <h2 className="font-semibold text-white">
                Create your first project
              </h2>

              <input
                value={newProjectName}
                onChange={(event) =>
                  setNewProjectName(event.target.value)
                }
                placeholder="Project name"
                className="mt-3 w-full rounded-lg border border-white/10 bg-[#0b1017] px-3 py-2 text-sm text-white"
              />

              <button
                type="button"
                onClick={handleCreateProject}
                disabled={loading}
                className="mt-3 w-full rounded-lg bg-cyan-500 px-3 py-2 text-sm font-semibold text-slate-950 disabled:opacity-50"
              >
                Create project
              </button>
            </div>
          )}

          {drawing && (
            <div className="space-y-3 rounded-xl border border-amber-400/20 bg-[#111923] p-4">
              <h2 className="font-semibold text-white">
                New area
              </h2>

              <label className="block text-sm text-slate-400">
                Area name
              </label>

              <input
                value={areaName}
                onChange={(event) =>
                  setAreaName(event.target.value)
                }
                placeholder="e.g. Research Zone A"
                className="w-full rounded-lg border border-white/10 bg-[#0b1017] px-3 py-2 text-sm text-white"
              />

              <label className="block text-sm text-slate-400">
                Description
              </label>

              <textarea
                value={description}
                onChange={(event) =>
                  setDescription(event.target.value)
                }
                rows={3}
                placeholder="Optional description"
                className="w-full rounded-lg border border-white/10 bg-[#0b1017] px-3 py-2 text-sm text-white"
              />

              <button
                type="button"
                onClick={saveArea}
                disabled={loading || draft.length < 3}
                className="w-full rounded-lg bg-cyan-500 px-3 py-2 text-sm font-semibold text-slate-950 disabled:opacity-50"
              >
                {loading ? "Saving..." : "Save area"}
              </button>
            </div>
          )}

          <div className="rounded-xl border border-white/10 bg-[#111923] p-4">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold text-white">
                Saved areas
              </h2>

              <span className="text-xs text-slate-400">
                {areas.length} total
              </span>
            </div>

            {loading && (
              <p className="mt-3 text-sm text-slate-400">
                Loading...
              </p>
            )}

            {!loading && areas.length === 0 && (
              <p className="mt-3 text-sm text-slate-500">
                No areas created yet.
              </p>
            )}

            <div className="mt-3 space-y-2">
              {areas.map((area) => (
                <div
                  key={area.id}
                  className={`rounded-lg border p-3 ${
                    selectedArea?.id === area.id
                      ? "border-cyan-400/50 bg-cyan-400/5"
                      : "border-white/10"
                  }`}
                >
                  <button
                    type="button"
                    onClick={() => selectArea(area)}
                    className="w-full text-left"
                  >
                    <p className="font-medium text-white">
                      {area.name}
                    </p>

                    <p className="mt-1 text-xs text-slate-400">
                      {area.area_sq_km.toFixed(4)} km²
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      Perimeter: {area.perimeter_m.toFixed(1)} m
                    </p>
                  </button>

                  <button
                    type="button"
                    onClick={() => deleteArea(area)}
                    className="mt-2 text-xs text-red-400 hover:text-red-300"
                  >
                    Delete area
                  </button>
                </div>
              ))}
            </div>
          </div>

          {selectedArea && (
            <div className="rounded-xl border border-white/10 bg-[#111923] p-4">
              <h2 className="font-semibold text-white">
                Area measurements
              </h2>

              <div className="mt-3 space-y-3">
                <div>
                  <p className="text-xs text-slate-400">
                    Area
                  </p>
                  <p className="text-lg font-semibold text-cyan-300">
                    {selectedArea.area_sq_km.toFixed(4)} km²
                  </p>
                </div>

                <div>
                  <p className="text-xs text-slate-400">
                    Area in square metres
                  </p>
                  <p className="text-sm text-white">
                    {selectedArea.area_sq_m.toLocaleString(
                      undefined,
                      { maximumFractionDigits: 2 },
                    )} m²
                  </p>
                </div>

                <div>
                  <p className="text-xs text-slate-400">
                    Perimeter
                  </p>
                  <p className="text-sm text-white">
                    {selectedArea.perimeter_m.toLocaleString(
                      undefined,
                      { maximumFractionDigits: 2 },
                    )} m
                  </p>
                </div>
              </div>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
