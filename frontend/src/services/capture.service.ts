import { api } from "@/lib/api";

export type CaptureStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed";

export interface Capture {
  id: string;
  project_id: string;
  area_id: string;
  data_source_id: string | null;
  created_by: string;
  status: CaptureStatus;
  config: Record<string, unknown>;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface Dataset {
  id: string;
  project_id: string;
  capture_id: string;
  name: string;
  format: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export const captureService = {
    async create(
      projectId: string,
      areaId: string,
      options?: {
        provider?: "geojson" | "stac";
        startDate?: string;
        endDate?: string;
        maxCloudCover?: number;
      },
    ): Promise<Capture> {
      const provider = options?.provider ?? "geojson";

      const response = await api.post<Capture>(
        `/projects/${projectId}/captures/`,
        {
          area_id: areaId,
          config: {
            provider,
            capture_type:
              provider === "stac"
                ? "satellite_imagery"
                : "area_boundary",
          },
          ...(provider === "stac"
            ? {
                start_date: options?.startDate,
                end_date: options?.endDate,
                max_cloud_cover: options?.maxCloudCover ?? 30,
              }
            : {}),
        },
      );

      return response.data;
    },

  async list(projectId: string): Promise<Capture[]> {
    const response = await api.get<Capture[]>(
      `/projects/${projectId}/captures/`,
    );

    return response.data;
  },

  async get(
    projectId: string,
    captureId: string,
  ): Promise<Capture> {
    const response = await api.get<Capture>(
      `/projects/${projectId}/captures/${captureId}`,
    );

    return response.data;
  },

  async getDatasets(
    projectId: string,
    captureId: string,
  ): Promise<Dataset[]> {
    const response = await api.get<Dataset[]>(
      `/projects/${projectId}/captures/${captureId}/datasets`,
    );

    return response.data;
  },
};