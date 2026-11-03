
import { api } from "@/lib/api";

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface RegisterPayload {
  email: string;
  full_name: string;
  password: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export const authService = {
  async register(payload: RegisterPayload): Promise<User> {
    const response = await api.post<User>(
      "/api/v1/auth/register",
      payload,
    );

    return response.data;
  },

  async login(payload: LoginPayload): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>(
      "/api/v1/auth/login",
      payload,
    );

    sessionStorage.setItem(
      "aleph_access_token",
      response.data.access_token,
    );

    return response.data;
  },

  async refresh(): Promise<boolean> {
    try {
      const response = await api.post<AuthResponse>(
        "/api/v1/auth/refresh",
      );

      sessionStorage.setItem(
        "aleph_access_token",
        response.data.access_token,
      );

      return true;
    } catch {
      sessionStorage.removeItem("aleph_access_token");
      return false;
    }
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>("/api/v1/auth/me");
    return response.data;
  },

  async logout(): Promise<void> {
    try {
      await api.post("/api/v1/auth/logout");
    } finally {
      sessionStorage.removeItem("aleph_access_token");
    }
  },
};
