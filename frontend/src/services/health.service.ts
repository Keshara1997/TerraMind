
import { api } from "@/lib/api";

export interface HealthResponse {
  status: string;
  application?: string;
  environment?: string;
  service?: string;
  database?: string;
  connection?: string;
}

export async function getApplicationHealth(): Promise<HealthResponse> {
  const response = await api.get<HealthResponse>("/health");
  return response.data;
}

export async function getDatabaseHealth(): Promise<HealthResponse> {
  const response = await api.get<HealthResponse>("/health/database");
  return response.data;
}

export async function getRedisHealth(): Promise<HealthResponse> {
  const response = await api.get<HealthResponse>("/health/redis");
  return response.data;
}
