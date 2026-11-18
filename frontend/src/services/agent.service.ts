import api from "@/lib/api";

export interface AgentQuestionRequest {
  question: string;
}

export interface AgentQuestionResponse {
  answer: string;
}

export const agentService = {
  async ask(
    projectId: string,
    payload: AgentQuestionRequest
  ): Promise<AgentQuestionResponse> {
    const response = await api.post(
      `/api/v1/ai/projects/${projectId}/agent`,
      payload
    );

    return response.data;
  },
};