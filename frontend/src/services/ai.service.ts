import api from "@/lib/api";

export interface AIQuestionRequest {
  question: string;
  start_date?: string;
  end_date?: string;
  area_id?: string;
}

export interface AIQuestionResponse {
  project_id: string;
  question: string;
  answer: string;
  observations_used: number;
  model: string;
}

export interface EnvironmentalReportResponse {
  project_id: string;
  title: string;
  period_start: string;
  period_end: string;
  observations_used: number;
  report: string;
}

export const aiService = {
  async ask(
    projectId: string,
    payload: AIQuestionRequest,
  ): Promise<AIQuestionResponse> {
    const response = await api.post(
      `/ai/projects/${projectId}/ask`,
      payload,
    );

    return response.data;
  },

  async generateReport(
    projectId: string,
    startDate: string,
    endDate: string,
    areaId?: string,
  ): Promise<EnvironmentalReportResponse> {
    const response = await api.post(
      `/ai/projects/${projectId}/environmental-report`,
      {
        start_date: startDate,
        end_date: endDate,
        area_id: areaId,
      },
    );

    return response.data;
  },
};