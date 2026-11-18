import api from "@/lib/api";

export interface NDVITimeSeriesPoint {
  dataset_id: string;
  capture_id: string;
  acquisition_date: string;
  mean: number | null;
  minimum: number | null;
  maximum: number | null;
  median: number | null;
  valid_pixels: number | null;
}

export interface NDVITimeSeriesResponse {
  project_id: string;
  area_id: string | null;
  start_date: string | null;
  end_date: string | null;
  total_observations: number;
  points: NDVITimeSeriesPoint[];
}

export const analysisService = {
  async getNDVITimeSeries(
    projectId: string,
    startDate?: string,
    endDate?: string,
    areaId?: string,
  ): Promise<NDVITimeSeriesResponse> {
    const response = await api.get(
      `/api/v1/analysis/projects/${projectId}/ndvi-time-series`,
      {
        params: {
          start_date: startDate || undefined,
          end_date: endDate || undefined,
          area_id: areaId || undefined,
        },
      },
    );

    return response.data;
  },

  async createNDVIChange(
    projectId: string,
    beforeDatasetId: string,
    afterDatasetId: string,
    threshold = 0.1,
  ) {
    const response = await api.post(
      `/api/v1/analysis/projects/${projectId}/ndvi-change`,
      {
        before_dataset_id: beforeDatasetId,
        after_dataset_id: afterDatasetId,
        threshold,
      },
    );

    return response.data;
  },
};