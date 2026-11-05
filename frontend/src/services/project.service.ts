
import { api } from "@/lib/api";

export interface Project {
  id: string;
  owner_id: string | null;
  name: string;
  description: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  name: string;
  description?: string | null;
}

export const projectService = {
  async list(): Promise<Project[]> {
    const response = await api.get<Project[]>("/api/v1/projects/");
    return response.data;
  },

  async create(payload: ProjectCreate): Promise<Project> {
    const response = await api.post<Project>(
      "/api/v1/projects/",
      payload,
    );

    return response.data;
  },
};
