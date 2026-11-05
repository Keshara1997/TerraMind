
import { api } from "@/lib/api";

export type AreaGeometry =
  | {
      type: "Polygon";
      coordinates: number[][][];
    }
  | {
      type: "MultiPolygon";
      coordinates: number[][][][];
    };

export interface Area {
  id: string;
  project_id: string;
  name: string;
  description: string | null;
  geometry: AreaGeometry;
  area_sq_m: number;
  area_sq_km: number;
  perimeter_m: number;
  created_at: string;
}

export interface AreaCreate {
  name: string;
  description?: string | null;
  geometry: AreaGeometry;
}

export interface AreaUpdate {
  name?: string;
  description?: string | null;
  geometry?: AreaGeometry;
}

const projectPath = (projectId: string) =>
  `/api/v1/projects/${projectId}/areas/`;

export const areaService = {
  async list(projectId: string): Promise<Area[]> {
    const response = await api.get<Area[]>(projectPath(projectId));
    return response.data;
  },

  async create(
    projectId: string,
    payload: AreaCreate,
  ): Promise<Area> {
    const response = await api.post<Area>(
      projectPath(projectId),
      payload,
    );

    return response.data;
  },

  async get(
    projectId: string,
    areaId: string,
  ): Promise<Area> {
    const response = await api.get<Area>(
      `${projectPath(projectId)}${areaId}`,
    );

    return response.data;
  },

  async update(
    projectId: string,
    areaId: string,
    payload: AreaUpdate,
  ): Promise<Area> {
    const response = await api.patch<Area>(
      `${projectPath(projectId)}${areaId}`,
      payload,
    );

    return response.data;
  },

  async delete(
    projectId: string,
    areaId: string,
  ): Promise<void> {
    await api.delete(
      `${projectPath(projectId)}${areaId}`,
    );
  },

  async findIntersections(
    projectId: string,
    geometry: AreaGeometry,
  ): Promise<Area[]> {
    const response = await api.post<Area[]>(
      `${projectPath(projectId)}intersections`,
      { geometry },
    );

    return response.data;
  },
};
