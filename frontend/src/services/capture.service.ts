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
        `/api/v1/projects/${projectId}/captures/`,
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
      `/api/v1/projects/${projectId}/captures/`,
    );

    return response.data;
  },

  async get(
    projectId: string,
    captureId: string,
  ): Promise<Capture> {
    const response = await api.get<Capture>(
      `/api/v1/projects/${projectId}/captures/${captureId}`,
    );

    return response.data;
  },

  async getDatasets(
    projectId: string,
    captureId: string,
  ): Promise<Dataset[]> {
    const response = await api.get<Dataset[]>(
      `/api/v1/projects/${projectId}/captures/${captureId}/datasets`,
    );

    return response.data;
  },


    async processNDVI(
    projectId: string,
    captureId: string,
    sourceDatasetId: string,
    itemId: string,
  ) {
    const response = await api.post(
      `/api/v1/projects/${projectId}/captures/${captureId}/ndvi`,
      {
        source_dataset_id: sourceDatasetId,
        item_id: itemId,
      },
    );

    return response.data;
  },

  async downloadUrl(
    projectId: string,
    captureId: string,
    datasetId: string,
  ): Promise<string> {
    return (
      `${api.defaults.baseURL}/api/v1/projects/${projectId}` +
      `/captures/${captureId}/datasets/${datasetId}/download`
    );
  },


  async download(
  projectId: string,
  captureId: string,
  datasetId: string,
): Promise<Blob> {
  const response = await api.get(
    `/api/v1/projects/${projectId}/captures/${captureId}/datasets/${datasetId}/download`,
    { responseType: "blob" },
  );

  return response.data;
},


};