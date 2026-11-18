import { api } from "@/lib/api";

export interface RasterInfo {
  id: string;
  name: string;
  format: string;
  crs: string | null;
  bounds: {
    left: number;
    bottom: number;
    right: number;
    top: number;
  } | null;
  statistics: {
    min: number;
    max: number;
    mean: number;
    median: number;
    valid_pixels: number;
    total_pixels: number;
  } | null;
  file_size_bytes: number | null;
  content_type: string | null;
}

export const rasterService = {
  async getInfo(
    projectId: string,
    captureId: string,
    datasetId: string,
  ): Promise<RasterInfo> {
    const response = await api.get<RasterInfo>(
      `/projects/${projectId}/captures/${captureId}/datasets/${datasetId}/raster-info`,
    );

    return response.data;
  },

  tilePath(
    projectId: string,
    captureId: string,
    datasetId: string,
  ): string {
    return (
      `/projects/${projectId}/captures/${captureId}` +
      `/datasets/${datasetId}/tiles/{z}/{x}/{y}.png`
    );
  },
};